# ⚖️ NyayBot — Multilingual AI Legal Document Assistant for India

<p align="center">
  <strong>"Every Indian can vote. Not every Indian can understand the contract they sign."</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI" />
  <img src="https://img.shields.io/badge/Next.js%2014-000000?style=for-the-badge&logo=next.js&logoColor=white" alt="Next.js" />
  <img src="https://img.shields.io/badge/Google_Gemini-8E75B2?style=for-the-badge&logo=google&logoColor=white" alt="Google Gemini" />
  <img src="https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white" alt="Tailwind CSS" />
  <img src="https://img.shields.io/badge/TypeScript-3178C6?style=for-the-badge&logo=typescript&logoColor=white" alt="TypeScript" />
  <img src="https://img.shields.io/badge/Render-46E3B7?style=for-the-badge&logo=render&logoColor=white" alt="Render" />
  <img src="https://img.shields.io/badge/Made%20in%20India-🇮🇳-orange?style=for-the-badge" alt="Made in India" />
</p>

---

## 📌 1. What is NyayBot?

**NyayBot (न्यायबॉट)** is an AI-powered legal document analysis and translation assistant designed for Indian citizens. It helps people understand contracts (such as rental leases, employment agreements, and loan documents) with **plain-language summaries, an AI-generated risk rating (1–10), potential red flags, and conversational Q&A in 11 Indian languages**. AI output can be incomplete or inaccurate; it is not legal advice.

---

## 🎯 2. Why NyayBot? (The Problem)

* **Complex language**: Contracts and notices can use dense terminology that is difficult for non-specialists to interpret.
* **Potentially one-sided terms**: Important obligations, payment rules, notice periods, or restrictions may be hard to spot in lengthy documents.
* **Access to guidance**: Some people may find it difficult or expensive to get timely help understanding routine documents.
* **Language barriers**: People may need explanations in languages other than the one used to draft a document.

**NyayBot aims to make an initial, plain-language explanation more accessible. It does not replace legal advice, and processing time and availability depend on the configured services.**

---

## ⚙️ 3. How It Works (Pipeline & Architecture)

```
┌─────────────────┐       ┌────────────────────────┐       ┌────────────────────────┐
│  Upload Legal   │ ----> │  PyMuPDF & LangDetect  │ ----> │   Parallel Execution   │
│   Document PDF  │       │  Text Clean & Chunking │       │     (Promise.all)      │
└─────────────────┘       └────────────────────────┘       └───────────┬────────────┘
                                                                       │
        ┌──────────────────────────────────────────────────────────────┴───────────────────────────┐
        ▼                                                              ▼                           ▼
┌─────────────────────────────┐                                ┌───────────────┐           ┌───────────────┐
│ Google Gemini Risk Engine   │                                │ Gemini 5-Pt   │           │ In-Memory RAG │
│ - Score 1-10 (Safe/Risky)   │                                │ Plain Summary │           │ Chunk Storage │
│ - Severity (High/Med/Low)   │                                └───────┬───────┘           └───────┬───────┘
│ - Indian Law Context Checks │                                        │                           │
└──────────────┬──────────────┘                                        │                           │
               │                                                       ▼                           ▼
               └────────────────────────────────────────────────> ┌────────────────────────────────────────┐
                                                                  │   Interactive Multilingual UI Screen   │
                                                                  │   - Animated Risk Score Gauge          │
                                                                  │   - Expandable Clause Flags Cards      │
                                                                  │   - Instant Speech (TTS) Audio 🔊      │
                                                                  │   - Grounded RAG Chat with Citations 💬│
                                                                  └────────────────────────────────────────┘
```

1. **PDF Ingestion & Text Extraction**: Extracts clean text from uploaded PDFs using `PyMuPDF`, performs language detection, and creates overlapping text chunks. Only PDFs with selectable text are supported.
2. **Parallel Processing**: The frontend concurrently asks the API to index document chunks, analyse risks, and generate a summary.
3. **Indian Legal Risk Analysis**: Google Gemini reviews the document for potentially concerning terms, classifies findings (`HIGH`, `MEDIUM`, `LOW`), and may suggest relevant Indian law and questions for a lawyer. These suggestions are not verified legal conclusions.
4. **Document Q&A**: The backend ranks cached text chunks by token overlap and sends relevant excerpts to Gemini. This is lightweight keyword retrieval, not a semantic/vector embedding index.

---

## ✨ 4. Key Features

- 🟢 **Animated Risk Score Gauge (1–10)**: Instant numerical risk rating (`SAFE`, `CAUTION`, `RISKY`) with signing recommendations (`SAFE_TO_SIGN`, `REVIEW_RECOMMENDED`, `DO_NOT_SIGN`).
- 🚩 **Predatory Clause Redlining**: Detailed inspection cards showing exact quoted clause text, a 10th-grade plain-language explanation, applicable Indian law (e.g. Model Tenancy Act, Indian Contract Act), and a specific question to ask an advocate.
- 📝 **5-Bullet Plain-Language Summary**: Distills obligations, deadlines, and financial amounts into five crisp bullet points.
- 💬 **Multilingual Document Q&A**: Conversational interface with keyword-ranked excerpts and cited source chunks.
- 🔊 **Indian Text-to-Speech (TTS) & Voice Input (STT)**: Listen to document summaries and chat answers in native Indian accents via Bhashini & Web Speech API.
- 📄 **Exportable Summary Card**: Centered modal with smooth scrolling and one-click clipboard copying.
- 🔒 **Transient App State**: NyayBot does not save documents to an application database. See [Privacy & data handling](#-10-privacy--data-handling) for important limits and third-party processing.

---

## 🌐 5. Supported Languages

| Code | Language | Native Script |
|---|---|---|
| `en` | English | English |
| `hi` | Hindi | हिंदी |
| `te` | Telugu | తెలుగు |
| `ta` | Tamil | தமிழ் |
| `kn` | Kannada | ಕನ್ನಡ |
| `bn` | Bengali | বাংলা |
| `mr` | Marathi | मराठी |
| `gu` | Gujarati | ગુજરાતી |
| `ml` | Malayalam | മലയാളം |
| `pa` | Punjabi | ਪੰਜਾਬੀ |
| `or` | Odia | ଓଡ଼ିଆ |

---

## 💻 6. Tech Stack

### Frontend
- **Framework**: [Next.js 16](https://nextjs.org/) (App Router)
- **UI & Styling**: [Tailwind CSS](https://tailwindcss.com/)
- **State Management**: [Zustand](https://github.com/pmndrs/zustand) (in-memory state only)
- **Language & Types**: TypeScript, React 19
- **Voice APIs**: Web Speech API (`SpeechRecognition`, `SpeechSynthesis`)

### Backend
- **Framework**: [FastAPI](https://fastapi.tiangolo.com/) (Python 3.11+)
- **LLM Engine**: [Google Gemini API](https://ai.google.dev/) (`google-genai` SDK)
- **Document Processing**: [PyMuPDF](https://pymupdf.readthedocs.io/) (`fitz`), `langdetect`
- **Translation & TTS**: Google Gemini + [Bhashini](https://bhashini.gov.in/) (Govt. of India)
- **Server**: [Uvicorn](https://www.uvicorn.org/)

---

## ☁️ 7. Deploy to Render (Step-by-Step)

This repository includes a `render.yaml` Blueprint for the FastAPI backend and Next.js frontend. Configure the backend's `CORS_ORIGINS` as a comma-separated list of exact frontend origins; the Blueprint uses `https://nyaybot-frontend.onrender.com`.

### Method A: Blueprint Deployment (Recommended)

1. Sign up / Log in to [Render.com](https://render.com/).
2. In the top navigation, click **New +** and select **Blueprint**.
3. Connect your GitHub repository: `https://github.com/maruthi-26/Nyay_Bot`.
4. Render will read `render.yaml` and discover both services:
   - `nyaybot-backend` (Python Web Service)
   - `nyaybot-frontend` (Node Web Service)
5. Under Environment Variables:
   - For `nyaybot-backend`: Enter your `GEMINI_API_KEY` (and optionally `GOOGLE_API_KEY`, `BHASHINI_API_KEY`, and `BHASHINI_USER_ID`).
   - For `nyaybot-backend`: Set `CORS_ORIGINS` to the exact origin of your deployed frontend. Do not use `*`.
   - For `nyaybot-frontend`: Set `NEXT_PUBLIC_API_URL` to `https://nyaybot-backend.onrender.com` (or your backend URL).
6. Click **Apply**. Render will automatically build and deploy both services!

---

### Method B: Manual Web Service Deployment

#### 1. Deploy the Backend:
- Click **New +** $\rightarrow$ **Web Service**.
- Select the `Nyay_Bot` repository.
- Configure:
  - **Name**: `nyaybot-backend`
  - **Root Directory**: `backend`
  - **Runtime**: `Python`
  - **Build Command**: `pip install -r requirements.txt`
  - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- Under **Environment Variables**, add:
  - `GEMINI_API_KEY` = `your_gemini_api_key`
  - `GOOGLE_API_KEY` = `your_gemini_api_key`
  - `CORS_ORIGINS` = comma-separated exact frontend origin(s), e.g. `https://nyaybot-frontend.onrender.com`
- Click **Create Web Service**. Note the deployed backend URL (e.g. `https://nyaybot-backend.onrender.com`).

#### 2. Deploy the Frontend:
- Click **New +** $\rightarrow$ **Web Service**.
- Select the `Nyay_Bot` repository.
- Configure:
  - **Name**: `nyaybot-frontend`
  - **Root Directory**: `frontend`
  - **Runtime**: `Node`
  - **Build Command**: `npm ci && npm run build`
  - **Start Command**: `npm start`
- Under **Environment Variables**, add:
  - `NEXT_PUBLIC_API_URL` = `https://nyaybot-backend.onrender.com`
- Click **Create Web Service**. Your app is now live!

---

## 🚀 8. Local Setup & Quickstart

### Prerequisites
- **Node.js** (v20.9+)
- **Python** (3.11+)
- **Google Gemini API Key** (Free at [Google AI Studio](https://aistudio.google.com/))

### Step 1: Clone Repository
```bash
git clone https://github.com/maruthi-26/Nyay_Bot.git
cd Nyay_Bot
```

### Step 2: Backend Setup
```bash
cd backend
python -m venv venv

# Windows
.\venv\Scripts\Activate.ps1
# Mac/Linux
source venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
# Edit .env and paste your GEMINI_API_KEY

uvicorn main:app --reload --port 8000
```
> Backend runs at `http://localhost:8000`. Swagger API docs at `http://localhost:8000/docs`. `CORS_ORIGINS` defaults to `http://localhost:3000`; set it to a comma-separated list of exact origins when deploying.

### Step 3: Frontend Setup
```bash
cd ../frontend
npm ci
npm run dev
```
> Frontend runs at `http://localhost:3000`.

### Verification

Run the backend guard tests with `python -m unittest discover -s backend/tests -v`, then build the production frontend with `npm ci && npm run build` from `frontend`.

---

## 📡 9. API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | API status & healthcheck |
| `POST` | `/upload` | Ingests PDF, extracts text, generates chunks & `doc_id` |
| `POST` | `/embed` | Caches validated document chunks in process memory |
| `POST` | `/analyse` | AI risk clause analysis (1–10 score, verdict, flags) |
| `POST` | `/summarise` | 5-bullet plain-language summary in target language |
| `POST` | `/ask` | Grounded RAG Q&A with auto-index recovery & citations |
| `POST` | `/translate` | Translates legal text into one of 11 supported languages |
| `POST` | `/speak` | Requests Bhashini TTS when configured; otherwise directs the client to browser speech |
| `POST` | `/generate-summary-card` | Generates a plain-language summary card |
| `GET` | `/languages` | Returns list of supported Indian languages |
| `GET` | `/risk-colour` | Returns color code, emoji, and badge for a risk score |

---

## 🔒 10. Privacy & Data Handling

- The frontend keeps the active document, analysis, and chat in **in-memory application state**, not browser local storage. On first load after this change, it removes the older `nyaybot-session` local-storage entry created by previous versions.
- The backend has no document database. Extracted text and the RAG chunk cache are transient process memory; the cache is capped at 100 documents and is lost on process restart. Multipart upload parsing may use temporary server files, depending on the runtime.
- Document text is sent to the configured Gemini service for analysis, summaries, Q&A, or translation; translation and TTS may also send text to Bhashini when configured. Review those providers' terms and retention policies before uploading sensitive documents.
- The API currently has **no user authentication or per-user document authorization**. CORS restricts browser origins but is not authentication and does not prevent direct API calls. Do not treat a document ID as an access-control mechanism. For public production use, place the API behind abuse controls and an authenticated gateway.
- Uploaded PDFs are limited to 10 MB, 300 pages, and 100,000 extracted characters. The backend accepts PDFs with extractable text; scanned-image OCR is not implemented.

## 🧭 Upgrade Roadmap

The repository is upgraded to patched Next.js 16 / React 19 and now validates request sizes, restricts CORS, bounds its in-memory cache, and avoids persisting legal documents in the browser. Before handling sensitive or high-volume production traffic, prioritize:

1. Add user authentication and document-level authorization, then isolate cached documents by owner.
2. Add distributed rate limiting, request timeouts, and spend limits at an API gateway; the current in-process cache and controls are not shared across replicas.
3. Add backend unit/API tests, automated dependency auditing, and CI checks for type checking and builds.
4. Add OCR only with clear retention controls; improve retrieval with tested semantic search and citations tied to source pages.
5. Add privacy/retention disclosures and evaluate Gemini/Bhashini data processing terms for the intended deployment.

---

## ⚖️ 11. Legal Disclaimer

> **NyayBot is an educational and information aid, not a law firm.**  
> The summaries, risk scores, and answers provided by NyayBot are generated using artificial intelligence and are intended solely for general informational understanding. NyayBot does not provide formal legal advice. For binding decisions, disputes, or contract execution, always consult a qualified advocate or legal professional.

---

<p align="center">
  Built with ❤️ for Indian citizens • Powered by Google Gemini
</p>
