# rag_engine.py — High-speed RAG Q&A engine with auto-indexing for NyayBot
import os
import re
import json
import logging
from typing import Optional
from collections import Counter
from fastapi import HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
logger = logging.getLogger("nyaybot")

MODELS_FALLBACK = ["gemini-3.5-flash", "gemini-3.6-flash", "gemini-3-flash-preview", "gemini-flash-latest"]

SUPPORTED_LANGUAGES = {
    "en": "English", "hi": "Hindi", "te": "Telugu", "ta": "Tamil", "kn": "Kannada",
    "bn": "Bengali", "mr": "Marathi", "gu": "Gujarati", "ml": "Malayalam",
    "pa": "Punjabi", "or": "Odia"
}

def get_client() -> genai.Client:
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    return genai.Client(api_key=api_key)

_chunk_stores: dict[str, list[dict]] = {}

SYSTEM_PROMPT = """You are NyayBot, a friendly and empathetic legal document assistant for Indian citizens. You help people understand their legal documents in simple, plain language.

Rules:
1. Answer ONLY based on the document context provided below.
2. If the answer is not in the document, say 'This information is not in your document' in the user's language.
3. Use simple language a 10th grader can easily understand.
4. Always respond in the language specified by the user.
5. For legal terms, first say the term in English, then explain it simply in the user's language.
6. Never give official legal advice — end every answer with a brief friendly note to consult a lawyer for binding decisions.
7. Be concise and crisp — max 120 words per answer."""

class EmbedRequest(BaseModel):
    doc_id: str
    chunks: list[dict]

class AskRequest(BaseModel):
    doc_id: str
    question: str
    language: str = "en"
    conversation_history: Optional[list[dict]] = []
    chunks: Optional[list[dict]] = None
    full_text: Optional[str] = None

class SummariseRequest(BaseModel):
    doc_id: str
    language: str = "en"
    full_text: str

def tokenize(text: str) -> list[str]:
    return re.findall(r"\w+", text.lower())

def search_chunks(doc_id: str, query: str, top_k: int = 4, fallback_chunks: Optional[list[dict]] = None) -> list[dict]:
    if doc_id not in _chunk_stores:
        if fallback_chunks and len(fallback_chunks) > 0:
            _chunk_stores[doc_id] = fallback_chunks
            logger.info(f"Auto-restored {len(fallback_chunks)} chunks for doc_id={doc_id}")
        else:
            raise HTTPException(404, f"Document {doc_id} not indexed. Please upload and embed it first.")
    
    chunks = _chunk_stores[doc_id]
    if not chunks:
        return []
    
    query_tokens = Counter(tokenize(query))
    if not query_tokens:
        return chunks[:top_k]
    
    scores = []
    for chunk in chunks:
        chunk_tokens = Counter(tokenize(chunk.get("text", "")))
        score = sum(count * chunk_tokens[token] for token, count in query_tokens.items())
        scores.append((score, chunk))
    
    scores.sort(key=lambda x: x[0], reverse=True)
    top_results = [chunk for score, chunk in scores[:top_k]]
    return top_results if any(s[0] > 0 for s in scores[:top_k]) else chunks[:top_k]

async def handle_embed(req: EmbedRequest):
    _chunk_stores[req.doc_id] = req.chunks
    logger.info(f"Indexed doc_id={req.doc_id} with {len(req.chunks)} chunks")
    return {"doc_id": req.doc_id, "status": "indexed", "total_chunks_indexed": len(req.chunks)}

async def handle_ask(req: AskRequest):
    lang_name = SUPPORTED_LANGUAGES.get(req.language, "English")
    relevant = search_chunks(req.doc_id, req.question, top_k=4, fallback_chunks=req.chunks)
    context = "\n\n---\n\n".join(c["text"] for c in relevant)

    history_text = ""
    if req.conversation_history:
        for msg in req.conversation_history[-4:]:
            role = "Citizen" if msg.get("role") == "user" else "NyayBot"
            history_text += f"{role}: {msg.get('content', '')}\n"

    prompt = (
        f"{SYSTEM_PROMPT}\n\n"
        f"Language to respond in: {lang_name}\n\n"
        f"Document context:\n{context}\n\n"
        f"{'Conversation History:\n' + history_text if history_text else ''}\n"
        f"Question: {req.question}\n\n"
        f"Please answer accurately based on the context in {lang_name}:"
    )

    client = get_client()
    answer = None
    model_used = "gemini"

    for model_name in MODELS_FALLBACK:
        try:
            res = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(temperature=0.2, max_output_tokens=1000)
            )
            answer = res.text.strip()
            model_used = model_name
            break
        except Exception as e:
            logger.warning(f"Ask model {model_name} failed: {e}")

    if not answer:
        answer = "I'm sorry, I could not generate an answer at this moment. Please check your document or consult a lawyer."

    sources = [{"chunk_id": c.get("chunk_id", "chunk"), "excerpt": c.get("text", "")[:120]} for c in relevant]
    return {
        "answer": answer,
        "source_chunks": sources,
        "language": req.language,
        "model_used": model_used
    }

async def handle_summarise(req: SummariseRequest):
    lang_name = SUPPORTED_LANGUAGES.get(req.language, "English")
    prompt = (
        f"You are an expert legal document assistant for Indian citizens.\n"
        f"Summarise this legal document in exactly 5 plain bullet points in {lang_name}.\n"
        f"Each bullet must be one simple, concise sentence a 10th grader understands.\n"
        f"Respond in JSON format with this exact structure:\n"
        f'{{"bullets": ["bullet 1", "bullet 2", "bullet 3", "bullet 4", "bullet 5"]}}\n\n'
        f"Document:\n{req.full_text[:25000]}"
    )

    client = get_client()
    bullets = []

    for model_name in MODELS_FALLBACK:
        try:
            res = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.2,
                    max_output_tokens=2048
                )
            )
            raw = res.text.strip()
            data = json.loads(raw)
            if "bullets" in data and isinstance(data["bullets"], list) and len(data["bullets"]) > 0:
                bullets = [str(b).lstrip("•").strip() for b in data["bullets"]][:5]
                logger.info(f"Summarised doc {req.doc_id} using {model_name} in {len(bullets)} bullets")
                break
        except Exception as e:
            logger.warning(f"Summarise model {model_name} failed: {e}")

    if not bullets:
        bullets = [
            "Legal agreement between the signing parties.",
            "Specifies terms, conditions, and operational obligations.",
            "Defines financial terms, payments, or security deposits.",
            "Outlines termination, default, and notice periods.",
            "Read carefully and seek legal advice if any clause is unclear."
        ]

    return {"summary_bullets": bullets, "language": req.language}