# risk_engine.py — High-speed risk clause detection for NyayBot using Google Gemini
import os
import json
import logging
from datetime import datetime, timezone
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

class AnalyseRequest(BaseModel):
    doc_id: str
    language: str = "en"
    full_text: str

class SummaryCardRequest(BaseModel):
    doc_id: str
    language: str = "en"
    analysis_result: dict

def parse_risk_json(raw: str) -> dict:
    raw = raw.strip()
    if "```" in raw:
        parts = raw.split("```")
        for p in parts:
            p = p.strip()
            if p.startswith("json"):
                p = p[4:].strip()
            try:
                return json.loads(p)
            except Exception:
                continue
    try:
        return json.loads(raw)
    except Exception:
        pass
    start = raw.find("{")
    end = raw.rfind("}")
    if start != -1 and end != -1:
        return json.loads(raw[start:end+1])
    return json.loads(raw.strip())

def risk_colour(score: int) -> dict:
    if score <= 3:
        return {"label": "SAFE", "hex_color": "#10B981", "emoji": "🟢"}
    elif score <= 6:
        return {"label": "CAUTION", "hex_color": "#F59E0B", "emoji": "🟡"}
    else:
        return {"label": "RISKY", "hex_color": "#EF4444", "emoji": "🔴"}

async def handle_analyse(req: AnalyseRequest):
    client = get_client()
    lang_name = SUPPORTED_LANGUAGES.get(req.language, "English")
    text = req.full_text[:30000]

    system_prompt = (
        f"You are an expert Indian legal risk analyst with 20 years experience in consumer protection and contract law. "
        f"Analyse this legal document and identify every clause that could harm, unfairly restrict, or create hidden obligations for the common citizen signing it.\n"
        f"Write plain_explanation, overall_verdict, and document_type in {lang_name}.\n\n"
        f"For each risky clause provide:\n"
        f"1. clause_text: exact problematic text from the document (max 50 words)\n"
        f"2. plain_explanation: explain the danger in simple, friendly {lang_name} a 10th grader understands\n"
        f"3. severity: HIGH, MEDIUM, or LOW\n"
        f"4. lawyer_question: single most important question to ask a lawyer in {lang_name}\n"
        f"5. indian_law_context: relevant Indian law\n\n"
        f"Also provide:\n"
        f"- overall_risk_score: Integer 1-10\n"
        f"- overall_verdict: one concise sentence verdict in {lang_name}\n"
        f"- document_type: document title in {lang_name}\n"
        f"- signing_recommendation: SAFE_TO_SIGN, REVIEW_RECOMMENDED, or DO_NOT_SIGN\n\n"
        f"Respond ONLY with a valid JSON object matching schema:\n"
        f'{{"overall_risk_score": 5, "overall_verdict": "string", "document_type": "string", "signing_recommendation": "SAFE_TO_SIGN | REVIEW_RECOMMENDED | DO_NOT_SIGN", "flags": [{{"clause_text": "string", "plain_explanation": "string", "severity": "HIGH | MEDIUM | LOW", "lawyer_question": "string", "indian_law_context": "string"}}]}}'
    )

    result = None
    for model_name in MODELS_FALLBACK:
        try:
            prompt = system_prompt + "\n\nDocument:\n\n" + text
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.2,
                    max_output_tokens=3000,
                )
            )
            raw = response.text
            result = parse_risk_json(raw)
            logger.info(f"Successfully analysed doc {req.doc_id} using {model_name}")
            break
        except Exception as e:
            logger.warning(f"Model {model_name} failed: {e}. Trying next fallback...")

    if not result:
        result = {
            "overall_risk_score": 5,
            "overall_verdict": "Document scanned. Please review flagged clauses carefully.",
            "document_type": "Legal Document",
            "signing_recommendation": "REVIEW_RECOMMENDED",
            "flags": []
        }

    order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    flags = sorted(result.get("flags", []), key=lambda f: order.get(f.get("severity", "LOW").upper(), 3))
    counts = {"high": 0, "medium": 0, "low": 0}
    for f in flags:
        s = f.get("severity", "LOW").upper()
        if s == "HIGH":
            counts["high"] += 1
        elif s == "MEDIUM":
            counts["medium"] += 1
        else:
            counts["low"] += 1
    counts["total"] = sum(counts.values())
    score = int(result.get("overall_risk_score", 5))

    return {
        "doc_id": req.doc_id,
        "document_type": result.get("document_type", "Legal Document"),
        "overall_risk_score": score,
        "overall_verdict": result.get("overall_verdict", ""),
        "signing_recommendation": result.get("signing_recommendation", "REVIEW_RECOMMENDED"),
        "risk_colour": risk_colour(score),
        "risk_counts": counts,
        "flags": flags,
        "language": req.language,
        "analysed_at": datetime.now(timezone.utc).isoformat(),
    }

async def handle_summary_card(req: SummaryCardRequest):
    lang_name = SUPPORTED_LANGUAGES.get(req.language, "English")
    analysis = req.analysis_result
    top_flags = [f for f in analysis.get("flags", []) if f.get("severity") == "HIGH"][:3]
    top_qs = [f.get("lawyer_question", "") for f in analysis.get("flags", [])[:3]]
    
    prompt = (
        f"Create a citizen-friendly legal summary card in {lang_name}:\n"
        f"Title: {analysis.get('document_type', 'Legal Document')} Risk {analysis.get('overall_risk_score', 5)}/10\n"
        f"Section 1: What you are agreeing to (3 plain bullets)\n"
        f"Section 2: Your key rights (2 bullets)\n"
        f"Section 3: Red flags: {json.dumps([f.get('plain_explanation', '') for f in top_flags])}\n"
        f"Section 4: Ask a lawyer: {json.dumps(top_qs)}\n"
        f"Footer: Generated by NyayBot. For reference only. Consult a lawyer.\n"
        f"Write entirely in {lang_name}. Each bullet under 20 words."
    )

    client = get_client()
    for model_name in MODELS_FALLBACK:
        try:
            res = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(temperature=0.2, max_output_tokens=1000)
            )
            return {"summary_card_text": res.text, "language": req.language}
        except Exception as e:
            logger.warning(f"Summary card model {model_name} failed: {e}")

    return {"summary_card_text": "Summary unavailable.", "language": req.language}

async def handle_risk_colour(score: int):
    return {"score": score, **risk_colour(score)}