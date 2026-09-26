# NyayBot Backend — Run with: uvicorn main:app --reload --port 8000
import logging
import os
import uuid
import re
from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from langdetect import detect, LangDetectException
try:
    import pymupdf as fitz
except ImportError:
    import fitz

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("nyaybot")

app = FastAPI(title="NyayBot API", version="2.0")

MAX_PDF_SIZE_BYTES = 10 * 1024 * 1024
MAX_PDF_PAGES = 300
MAX_DOCUMENT_CHARS = 100_000

allowed_origins = [
    origin.strip().rstrip("/")
    for origin in os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
    if origin.strip()
]
if not allowed_origins or "*" in allowed_origins:
    raise RuntimeError("CORS_ORIGINS must contain explicit origins; wildcards are not allowed.")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

# ── text helpers ──────────────────────────────────────────────────────────────

def clean_text(raw: str) -> str:
    lines = raw.split("\n")
    cleaned = []
    for line in lines:
        line = line.strip()
        if re.match(r"^\d+$", line):
            continue
        if line:
            cleaned.append(line)
    return " ".join(cleaned)

def chunk_text(text: str, chunk_size: int = 600, overlap: int = 80):
    chunks, start, idx = [], 0, 1
    while start < len(text):
        end = min(start + chunk_size, len(text))
        if end < len(text):
            b = text.rfind(".", start, end)
            if b == -1:
                b = text.rfind(" ", start, end)
            if b >= start + chunk_size // 2:
                end = b + 1
        snippet = text[start:end].strip()
        if snippet:
            chunks.append({
                "chunk_id": f"chunk_{idx:03d}",
                "text": snippet,
                "start_char": start,
                "end_char": end
            })
            idx += 1
        if end >= len(text):
            break
        start = max(start + 1, end - overlap)
    return chunks

# ── endpoints ─────────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {"status": "NyayBot API running (Powered by Google Gemini)", "version": "2.0"}

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    if not (file.filename or "").lower().endswith(".pdf"):
        raise HTTPException(400, "Only PDF files are accepted.")
    content = await file.read(MAX_PDF_SIZE_BYTES + 1)
    if len(content) > MAX_PDF_SIZE_BYTES:
        raise HTTPException(413, "File size exceeds 10MB limit.")
    if not content.startswith(b"%PDF-"):
        raise HTTPException(422, "The uploaded file is not a valid PDF.")

    doc = None
    try:
        doc = fitz.open(stream=content, filetype="pdf")
        if doc.needs_pass:
            raise HTTPException(422, "This PDF is password-protected. Please remove the password and try again.")
        if doc.page_count > MAX_PDF_PAGES:
            raise HTTPException(413, f"PDFs are limited to {MAX_PDF_PAGES} pages.")
        page_texts = []
        total_chars = 0
        for page in doc:
            page_text = clean_text(page.get_text())
            total_chars += len(page_text) + (1 if page_texts else 0)
            if total_chars > MAX_DOCUMENT_CHARS:
                raise HTTPException(413, "Extracted document text exceeds the 100,000 character limit.")
            page_texts.append(page_text)
    except HTTPException:
        raise
    except Exception:
        logger.exception("Failed to parse uploaded PDF")
        raise HTTPException(422, "The uploaded PDF could not be read.")
    finally:
        if doc is not None:
            doc.close()

    full_text = " ".join(page_texts)
    if len(full_text.strip()) < 100:
        raise HTTPException(422, "This PDF contains only scanned images. Text extraction is not supported yet.")

    try:
        lang = detect(full_text[:500])
    except LangDetectException:
        lang = "en"

    chunks = chunk_text(full_text)
    doc_id = str(uuid.uuid4())
    logger.info("Uploaded doc_id=%s pages=%s chunks=%s", doc_id, len(page_texts), len(chunks))

    return {
        "doc_id": doc_id,
        "filename": file.filename or "document.pdf",
        "total_pages": len(page_texts),
        "total_chars": len(full_text),
        "total_chunks": len(chunks),
        "language_detected": lang,
        "full_text": full_text,
        "chunks": chunks,
    }

# Wire up RAG, Risk Engine, and Translate modules
from rag_engine import EmbedRequest, AskRequest, SummariseRequest, handle_embed, handle_ask, handle_summarise
from risk_engine import AnalyseRequest, SummaryCardRequest, handle_analyse, handle_summary_card, handle_risk_colour
from translate import TranslateRequest, SpeakRequest, handle_translate, handle_speak, handle_languages

@app.post("/embed")
async def embed(req: EmbedRequest):
    return await handle_embed(req)

@app.post("/ask")
async def ask(req: AskRequest):
    return await handle_ask(req)

@app.post("/summarise")
async def summarise(req: SummariseRequest):
    return await handle_summarise(req)

@app.post("/analyse")
async def analyse(req: AnalyseRequest):
    return await handle_analyse(req)

@app.post("/generate-summary-card")
async def summary_card(req: SummaryCardRequest):
    return await handle_summary_card(req)

@app.get("/risk-colour")
async def risk_colour_endpoint(score: int = Query(..., ge=1, le=10)):
    return await handle_risk_colour(score)

@app.post("/translate")
async def translate(req: TranslateRequest):
    return await handle_translate(req)

@app.post("/speak")
async def speak(req: SpeakRequest):
    return await handle_speak(req)

@app.get("/languages")
def languages():
    return handle_languages()
