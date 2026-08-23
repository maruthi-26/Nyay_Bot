# translate.py — High-speed multilingual translation + TTS for NyayBot powered by Google Gemini
import os
import time
import logging
import aiohttp
from typing import Optional
from pydantic import BaseModel
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
logger = logging.getLogger("nyaybot")

MODELS_FALLBACK = ["gemini-3.5-flash", "gemini-3.6-flash", "gemini-3-flash-preview", "gemini-flash-latest"]

LANGUAGES = {
    "en": {"name": "English", "native": "English"},
    "hi": {"name": "Hindi", "native": "हिंदी"},
    "te": {"name": "Telugu", "native": "తెలుగు"},
    "ta": {"name": "Tamil", "native": "தமிழ்"},
    "kn": {"name": "Kannada", "native": "ಕನ್ನಡ"},
    "bn": {"name": "Bengali", "native": "বাংলা"},
    "mr": {"name": "Marathi", "native": "मराठी"},
    "gu": {"name": "Gujarati", "native": "ગુજરાતી"},
    "ml": {"name": "Malayalam", "native": "മലയാളം"},
    "pa": {"name": "Punjabi", "native": "ਪੰਜਾਬੀ"},
    "or": {"name": "Odia", "native": "ଓଡ଼ିଆ"},
}

def get_client() -> genai.Client:
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    return genai.Client(api_key=api_key)

class TranslateRequest(BaseModel):
    text: str
    target_lang: str
    source_lang: str = "en"

class SpeakRequest(BaseModel):
    text: str
    lang: str

async def translate_with_gemini(text: str, target_lang: str) -> str:
    lang_name = LANGUAGES.get(target_lang, {}).get("name", "Hindi")
    prompt = (
        f"Translate the following legal/plain text accurately into natural, conversational {lang_name}.\n"
        f"Rules:\n"
        f"1. Keep crucial legal terms in English but immediately follow with their meaning in {lang_name} in parentheses if helpful.\n"
        f"2. Use simple conversational {lang_name} understandable by common people.\n"
        f"3. Preserve all numbers, dates, monetary amounts, and names exactly.\n"
        f"4. Return ONLY the translated text. No introductions, no notes, no explanations.\n\n"
        f"Text:\n{text}"
    )

    client = get_client()
    for model_name in MODELS_FALLBACK:
        try:
            res = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(temperature=0.2, max_output_tokens=600)
            )
            return res.text.strip()
        except Exception as e:
            logger.warning(f"Translation with {model_name} failed: {e}")

    return text

async def translate_text(text: str, target_lang: str, source_lang: str = "en") -> tuple[str, str]:
    if target_lang == source_lang or not text.strip():
        return text, "none"

    bhashini_key = os.getenv("BHASHINI_API_KEY", "")
    if bhashini_key and target_lang != "en":
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "pipelineTasks": [{"taskType": "translation", "config": {"language": {"sourceLanguage": source_lang, "targetLanguage": target_lang}}}],
                    "inputData": {"input": [{"source": text}]}
                }
                headers = {"userID": os.getenv("BHASHINI_USER_ID", ""), "ulcaApiKey": bhashini_key, "Content-Type": "application/json"}
                async with session.post(
                    "https://dhruva-api.bhashini.gov.in/services/inference/pipeline",
                    json=payload, headers=headers, timeout=aiohttp.ClientTimeout(total=3)
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        translated = data["pipelineResponse"][0]["output"][0]["target"]
                        return translated, "bhashini"
        except Exception as e:
            logger.warning(f"Bhashini failed: {e}, falling back to Gemini")

    translated = await translate_with_gemini(text, target_lang)
    return translated, "gemini"

async def text_to_speech(text: str, lang: str) -> tuple[Optional[str], str]:
    bhashini_key = os.getenv("BHASHINI_API_KEY", "")
    if bhashini_key:
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "pipelineTasks": [{"taskType": "tts", "config": {"language": {"sourceLanguage": lang}, "gender": "female"}}],
                    "inputData": {"input": [{"source": text}]}
                }
                headers = {"userID": os.getenv("BHASHINI_USER_ID", ""), "ulcaApiKey": bhashini_key, "Content-Type": "application/json"}
                async with session.post(
                    "https://dhruva-api.bhashini.gov.in/services/inference/pipeline",
                    json=payload, headers=headers, timeout=aiohttp.ClientTimeout(total=5)
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        audio_b64 = data["pipelineResponse"][0]["audio"][0]["audioContent"]
                        return audio_b64, "bhashini"
        except Exception as e:
            logger.warning(f"Bhashini TTS failed: {e}")
    return None, "browser_tts"

async def handle_translate(req: TranslateRequest):
    start = time.time()
    translated, provider = await translate_text(req.text, req.target_lang, req.source_lang)
    elapsed = int((time.time() - start) * 1000)
    return {
        "original_text": req.text,
        "translated_text": translated,
        "source_lang": req.source_lang,
        "target_lang": req.target_lang,
        "provider": provider,
        "translation_time_ms": elapsed,
    }

async def handle_speak(req: SpeakRequest):
    audio, provider = await text_to_speech(req.text, req.lang)
    return {
        "audio_base64": audio,
        "lang": req.lang,
        "char_count": len(req.text),
        "provider": provider,
        **({"message": "Use browser Web Speech API"} if audio is None else {}),
    }

def handle_languages():
    return [{"code": k, "name": v["name"], "native": v["native"]} for k, v in LANGUAGES.items()]