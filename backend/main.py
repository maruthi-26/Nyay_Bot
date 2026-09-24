# NyayBot Backend — Run with: uvicorn main:app --reload --port 8000
import os
import time
import logging
import secrets
import re
from collections import defaultdict, deque
from fastapi import FastAPI, Request, UploadFile, File, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from langdetect import detect, LangDetectException
try:
    import pymupdf as fitz
except ImportError:
    import fitz

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("nyaybot")

app = FastAPI(title="NyayBot API", version="2.1")

# SECURITY FIX: never combine wildcard origins with credentials.
# Configure explicit, comma-separated allowed origins in production.
ALLOWED_ORIGINS = [o.strip() for o in os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:3000"
).split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,          # API is tokenless; don't enable with wildcards
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

# SECURITY FIX: simple in-memory rate limiter to stop quota-abuse / cost-DoS
# on expensive LLM-backed endpoints. Use X-Forwarded-For cautiously behind a
# trusted proxy, or swap for slowapi/redis for multi-instance deployments.
RATE_LIMIT = int(os.getenv("RATE_LIMIT_PER_MIN", "30"))
_rate_buckets: dict[str, deque] = defaultdict(deque)

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    # SECURITY FIX: never raise inside BaseHTTPMiddleware (it escapes to the
    # global handler as a 500). Return the 429 response directly instead.
    if request.method != "OPTIONS" and request.url.path not in ("/", "/languages"):
        client_ip = request.client.host if request.client else "unknown"
        bucket = _rate_buckets[client_ip]
        now = time.monotonic()
        while bucket and now - bucket[0] > 60:
            bucket.popleft()
        if len(bucket) >= RATE_LIMIT:
            return JSONResponse(
                status_code=429,
                content={"detail": "Too many requests. Please slow down."},
                headers={"Retry-After": "60"},
            )
        bucket.append(now)
    response = await call_next(request)
    # SECURITY FIX: basic hardening headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    return response

@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    # SECURITY FIX: log internals, never leak them to the client.
    logger.exception("Unhandled error on %s %s", request.method, request.url.path)
    return JSONResponse(status_code=500, content={"detail": "Internal server error."})

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

MAX_UPLOAD_BYTES = int(os.getenv("MAX_UPLOAD_BYTES", str(10 * 1024 * 1024)))
MAX_PAGES = int(os.getenv("MAX_PDF_PAGES", "300"))

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    # SECURITY FIX: validate extension, declared MIME type, AND magic bytes.
    filename = file.filename or "document.pdf"
    if not filename.lower().endswith(".pdf"):
        raise HTTPException(400, "Only PDF files are accepted.")
    if file.content_type not in ("application/pdf", "application/octet-stream"):
        raise HTTPException(400, "Only PDF files are accepted.")

    # SECURITY FIX: read with a hard cap so oversized bodies can't exhaust RAM.
    content = await file.read(MAX_UPLOAD_BYTES + 1)
    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(413, "File size exceeds 10MB limit.")
    if not content.startswith(b"%PDF-"):
        raise HTTPException(400, "Only PDF files are accepted.")
    try:
        doc = fitz.open(stream=content, filetype="pdf")
        if doc.needs_pass:
            doc.close()
            raise HTTPException(422, "This PDF is password-protected. Please remove the password and try again.")
        # SECURITY FIX: cap page count to blunt decompression-bomb style PDFs.
        if doc.page_count > MAX_PAGES:
            doc.close()
            raise HTTPException(422, f"PDF has too many pages (limit {MAX_PAGES}).")
        pages = [{"page_num": i + 1, "raw_text": p.get_text()} for i, p in enumerate(doc)]
        doc.close()
    except HTTPException:
        raise
    except Exception as e:
        # SECURITY FIX: don't leak internal parser details to clients.
        logger.warning(f"PDF parse failed: {e}")
        raise HTTPException(422, "Could not read this PDF. It may be corrupted.")

    full_text = " ".join(clean_text(p["raw_text"]) for p in pages)
    if len(full_text.strip()) < 100:
        raise HTTPException(422, "This PDF contains only scanned images. Text extraction is not supported yet.")

    try:
        lang = detect(full_text[:500])
    except LangDetectException:
        lang = "en"

    chunks = chunk_text(full_text)
    # SECURITY FIX: unguessable, server-issued session id (secrets module),
    # and index the document server-side at upload time so /embed round-trips
    # and client-supplied doc_ids aren't required.
    doc_id = secrets.token_urlsafe(24)
    from rag_engine import store_chunks
    store_chunks(doc_id, chunks)
    logger.info(f"Uploaded doc_id={doc_id} pages={len(pages)} chunks={len(chunks)}")

    # SECURITY FIX: sanitize the echoed filename (strip path components and
    # control chars) so it can't spoof UI text; and cap its length.
    safe_filename = os.path.basename(filename).replace("\x00", "")[:200]

    return {
        "doc_id": doc_id,
        "filename": safe_filename,
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
    # SECURITY FIX: bound prompt size — this endpoint bills per token.
    if len(req.full_text) > 50_000:
        raise HTTPException(413, "Document text exceeds 50k character limit.")
    return await handle_summarise(req)

@app.post("/analyse")
async def analyse(req: AnalyseRequest):
    # SECURITY FIX: bound prompt size — this endpoint bills per token.
    if len(req.full_text) > 50_000:
        raise HTTPException(413, "Document text exceeds 50k character limit.")
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
