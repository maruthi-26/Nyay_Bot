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
  <img src="https://img.shields.io/badge/Made%20in%20India-🇮🇳-orange?style=for-the-badge" alt="Made in India" />
</p>

---

## 📌 1. What is NyayBot?

**NyayBot (न्यायबॉट)** is an AI-powered legal document analysis and translation assistant designed specifically for Indian citizens. It bridges the literacy, language, and legal jargon gap by transforming complex legal contracts (rental leases, employment agreements, loan documents, terms of service) into **plain-language summaries, interactive risk ratings (1–10), red-flagged predatory clauses, and conversational Q&A across 11 Indian languages**.

---

## 🎯 2. Why NyayBot? (The Problem)

* **800 Million+ Indians** enter into binding legal agreements (renting a home, accepting a job, taking personal loans) written in dense legal English that they cannot fully understand.
* **Predatory & One-Sided Clauses**: Leases and contracts often hide severe clauses—such as 24-month lock-in periods with total deposit forfeiture, warrantless landlord entry, or non-compete clauses that violate Section 27 of the Indian Contract Act.
* **Expensive Legal Advice**: Hiring an advocate to review standard contracts is unaffordable or inaccessible for most common citizens and gig workers.
* **Language Barrier**: Less than 10% of India's population is fluent in English, yet virtually all binding contracts are drafted in English.

**NyayBot solves this by providing free, instant, and citizen-friendly legal clarity in your mother tongue within seconds.**

---

## ⚙️ 3. How It Works (Pipeline & Architecture)

`
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
`

1. **PDF Ingestion & Text Extraction**: Extracts clean text from uploaded PDFs using PyMuPDF, performs language detection, and creates semantic overlapping chunks.
2. **High-Speed Parallel Processing**: Runs document embedding, risk evaluation, and plain-language summarization concurrently via Promise.all in ~5–7 seconds.
3. **Indian Legal Risk Analysis**: Leverages Google Gemini models with native JSON Schema output to identify unfair terms, classify severity (HIGH, MEDIUM, LOW), cite relevant Indian statutes, and formulate questions for a lawyer.
4. **Interactive Document RAG Chat**: Users can ask any question about their agreement in their native tongue and receive simple, context-grounded answers with document chunk citations.

---

## ✨ 4. Key Features

- 🟢 **Animated Risk Score Gauge (1–10)**: Instant numerical risk rating (SAFE, CAUTION, RISKY) with signing recommendations (SAFE_TO_SIGN, REVIEW_RECOMMENDED, DO_NOT_SIGN).
- 🚩 **Predatory Clause Redlining**: Detailed inspection cards showing exact quoted clause text, a 10th-grade plain-language explanation, applicable Indian law (e.g. Model Tenancy Act, Indian Contract Act), and a specific question to ask an advocate.
- 📝 **5-Bullet Plain-Language Summary**: Distills obligations, deadlines, and financial amounts into five crisp bullet points.
- 💬 **Multilingual Grounded Q&A**: Real-time conversational interface with automatic auto-index recovery and cited source excerpts.
- 🔊 **Indian Text-to-Speech (TTS) & Voice Input (STT)**: Listen to document summaries and chat answers in native Indian accents via Bhashini & Web Speech API.
- 📄 **Exportable Summary Card**: Centered modal with smooth scrolling and one-click clipboard copying.
- 🔒 **Zero Storage Privacy**: Documents are processed in-memory and are never stored on any persistent database.

---

## 🌐 5. Supported Languages

| Code | Language | Native Script |
|---|---|---|
| en | English | English |
| hi | Hindi | हिंदी |
| 	e | Telugu | తెలుగు |
| 	a | Tamil | தமிழ் |
| kn | Kannada | ಕನ್ನಡ |
| n | Bengali | বাংলা |
| mr | Marathi | मराठी |
| gu | Gujarati | ગુજરાતી |
| ml | Malayalam | മലയാളം |
| pa | Punjabi | ਪੰਜਾਬੀ |
| or | Odia | ଓଡ଼ିଆ |

---

## 💻 6. Tech Stack

### Frontend
- **Framework**: [Next.js 14](https://nextjs.org/) (App Router)
- **UI & Styling**: [Tailwind CSS](https://tailwindcss.com/)
- **State Management**: [Zustand](https://github.com/pmndrs/zustand) (with session persistence)
- **Language & Types**: TypeScript
- **Voice APIs**: Web Speech API (SpeechRecognition, SpeechSynthesis)

### Backend
- **Framework**: [FastAPI](https://fastapi.tiangolo.com/) (Python 3.11+)
- **LLM Engine**: [Google Gemini API](https://ai.google.dev/) (google-genai SDK)
- **Document Processing**: [PyMuPDF](https://pymupdf.readthedocs.io/) (itz), langdetect
- **Translation & TTS**: Google Gemini + [Bhashini](https://bhashini.gov.in/) (Govt. of India)
- **Server**: [Uvicorn](https://www.uvicorn.org/)

---

## 🚀 7. Quickstart & Installation Guide

### Prerequisites
- **Node.js** (v18+ recommended)
- **Python** (3.11, 3.12, or 3.13)
- **Google Gemini API Key** (Get free at [Google AI Studio](https://aistudio.google.com/))

---

### Step 1: Clone the Repository
`ash
git clone https://github.com/maruthi-26/Nyay_Bot.git
cd Nyay_Bot
`

---

### Step 2: Configure & Start the Backend

1. Navigate to the ackend folder:
   `ash
   cd backend
   `

2. Create a virtual environment and activate it:
   `ash
   # Windows (PowerShell)
   python -m venv venv
   .\venv\Scripts\Activate.ps1

   # macOS / Linux
   python3 -m venv venv
   source venv/bin/activate
   `

3. Install Python dependencies:
   `ash
   pip install -r requirements.txt
   `

4. Create .env file:
   `ash
   # Copy example template
   cp .env.example .env
   `
   Open ackend/.env and paste your Gemini API key:
   `env
   GEMINI_API_KEY=your_gemini_api_key_here
   GOOGLE_API_KEY=your_gemini_api_key_here
   BHASHINI_API_KEY=
   BHASHINI_USER_ID=
   `

5. Start the FastAPI server:
   `ash
   uvicorn main:app --reload --port 8000
   `
   > 🟢 Backend will be live at http://localhost:8000. Test interactive docs at http://localhost:8000/docs.

---

### Step 3: Configure & Start the Frontend

1. Open a new terminal and navigate to the rontend folder:
   `ash
   cd frontend
   `

2. Install npm dependencies:
   `ash
   npm install
   `

3. Start the Next.js development server:
   `ash
   npm run dev
   `
   > 🟢 Frontend will be live at http://localhost:3000.

---

## 📡 8. API Reference

| Method | Endpoint | Description |
|---|---|---|
| GET | / | API status & healthcheck |
| POST | /upload | Ingests PDF, extracts text, generates chunks & doc_id |
| POST | /embed | Builds vector index for document chunks |
| POST | /analyse | AI risk clause analysis (1–10 score, verdict, flags) |
| POST | /summarise | 5-bullet plain-language summary in target language |
| POST | /ask | Grounded RAG Q&A with auto-index recovery & citations |
| POST | /translate | Translates legal text into 10+ Indian languages |
| POST | /speak | Native Indian audio base64 generation via TTS |
| GET | /languages | Returns list of supported Indian languages |
| GET | /risk-colour | Returns color code, emoji, and badge for a risk score |

---

## 🔒 9. Privacy & Security

- **Zero Document Storage**: NyayBot operates completely in-memory. Uploaded document contents and extracted text are **never saved to disk or persistent databases**.
- **Ephemeral Sessions**: Chunk caches are tied to transient session IDs and cleared automatically.

---

## ⚖️ 10. Legal Disclaimer

> **NyayBot is an educational and information aid, not a law firm.**  
> The summaries, risk scores, and answers provided by NyayBot are generated using artificial intelligence and are intended solely for general informational understanding. NyayBot does not provide formal legal advice. For binding decisions, disputes, or contract execution, always consult a qualified advocate or legal professional.

---

<p align="center">
  Built with ❤️ for Indian citizens • Powered by Google Gemini
</p>
