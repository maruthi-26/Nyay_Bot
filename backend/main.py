# NyayBot Backend — Run with: uvicorn main:app --reload --port 8000
import logging
import uuid
import re
from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from langdetect import detect, LangDetectException
import fitz  # PyMuPDF

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("nyaybot")

app = FastAPI(title="NyayBot API", version="2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"status": "ok", "service": "NyayBot Backend", "version": "2.0"}

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
        end = start + chunk_size
        if end < len(text):
            b = text.rfind(".", start, end)
            if b == -1:
                b = text.rfind(" ", start, end)
            if b != -1:
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
        start = end - overlap
    return chunks

# ── endpoints ─────────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {"status": "NyayBot API running (Powered by Google Gemini)", "version": "2.0"}

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(400, "Only PDF files are accepted.")
    content = await file.read()
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(413, "File size exceeds 10MB limit.")
    try:
        doc = fitz.open(stream=content, filetype="pdf")
        if doc.needs_pass:
            raise HTTPException(422, "This PDF is password-protected. Please remove the password and try again.")
        pages = [{"page_num": i + 1, "raw_text": p.get_text()} for i, p in enumerate(doc)]
        doc.close()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))

    full_text = " ".join(clean_text(p["raw_text"]) for p in pages)
    if len(full_text.strip()) < 100:
        raise HTTPException(422, "This PDF contains only scanned images. Text extraction is not supported yet.")

    try:
        lang = detect(full_text[:500])
    except LangDetectException:
        lang = "en"

    chunks = chunk_text(full_text)
    doc_id = str(uuid.uuid4())
    logger.info(f"Uploaded doc_id={doc_id} pages={len(pages)} chunks={len(chunks)}")

    return {
        "doc_id": doc_id,
        "filename": file.filename,
        "total_pages": len(pages),
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
async def risk_colour_endpoint(score: int = Query(...)):
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
