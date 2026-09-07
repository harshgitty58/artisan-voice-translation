# Artisan AI Business Copilot — Speech Translation & Multilingual Catalog

This service implements **Table 007 (`product_translations`)** and the multilingual processing engine for the Artisan AI Business Copilot.

---

## 1. Module Overview

- **Table 007 — `product_translations`**:
  - Stores language-specific versions of product `name` and `description`.
  - MVP Languages: English (`en`), Hindi (`hi`), Marathi (`mr`).
  - Canonical product records remain in `products` (from `006_products`).
  - Strict uniqueness constraint: `UNIQUE(product_id, language_code)`.
  - Check constraints ensure no empty or whitespace-only names/descriptions.
  - Row Level Security (RLS) guarantees public visibility only for published products, while artisans can manage their own drafts and translations.
- **Translation & Speech Pipeline**:
  - Artisan voice input is transcribed using **Google Cloud Speech-to-Text**.
  - Product catalog translations (English, Hindi, Marathi) are generated via **Google Cloud Translation API**.
  - Built-in safe mock fallback allows instant local testing and offline development before configuring API keys.
- **FastAPI Microservice**:
  - Modular clean architecture with Pydantic v2 validation.
  - Interactive OpenAPI / Swagger UI at `/docs`.
  - Configured for 24/7 web service reinitialization on **Render** (free tier).

---

## 2. Project Structure

```
Speech Translation/
├── app/
│   ├── api/
│   │   └── v1/
│   │       └── translations.py      # Endpoints for catalog, translations & speech
│   ├── core/
│   │   └── config.py                # Environment and app settings
│   ├── schemas/
│   │   └── translation.py           # Pydantic models (Table 007 spec)
│   ├── services/
│   │   ├── speech_service.py        # Google Cloud Speech-to-Text client
│   │   ├── translation_service.py   # Google Cloud Translation client
│   │   └── supabase_service.py      # Supabase DB client with in-memory adapter
│   └── main.py                      # FastAPI application entrypoint
├── migrations/
│   └── 007_product_translations.sql # Safe idempotent Supabase SQL migration
├── .env.example                     # Environment template
├── Procfile                         # Render/PaaS start command
├── render.yaml                      # Render Blueprint configuration (Free Tier)
├── requirements.txt                 # Dependencies
├── run_server.py                    # Local server launcher
└── README.md
```

---

## 3. Environment Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure `.env`**:
   Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
   Add your keys:
   - `GOOGLE_CLOUD_API_KEY`: Your Google Cloud API Key enabled for **Cloud Speech-to-Text API** and **Cloud Translation API**.
   - `SUPABASE_URL` & `SUPABASE_ANON_KEY`: (Optional) Supabase credentials when ready to connect to PostgreSQL.

*(Note: If `GOOGLE_CLOUD_API_KEY` or Supabase keys are not set, the app runs gracefully using built-in artisan dictionary & mock responses for zero-friction local testing).*

---

## 4. Running Locally

Start the FastAPI server using the provided runner:
```bash
python run_server.py
```
Or directly via uvicorn:
```bash
uvicorn app.main:app --reload --port 8000
```
Open **http://localhost:8000/docs** to test all endpoints interactively.

---

## 5. Deploying to Render (Free Web Service)

Deploying to Render provides a persistent public HTTPS URL (e.g. `https://artisan-speech-translation.onrender.com`), automatic SSL, and persistent reinitialization on demand without maintaining local tunnels.

### Quick Setup on Render:
1. Log into [dashboard.render.com](https://dashboard.render.com).
2. Click **New +** &rarr; **Web Service** (or use **Blueprint** connecting your repo with `render.yaml`).
3. Connect your repository.
4. Set:
   - **Name**: `artisan-speech-translation`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: Free
5. Under **Environment Variables**, add:
   - `GOOGLE_CLOUD_API_KEY`: Your Google Cloud API Key
   - `SUPABASE_URL`: Your Supabase Project URL
   - `SUPABASE_ANON_KEY`: Your Supabase Anon Key

Your service will build automatically and be available at your assigned `.onrender.com` domain with full Swagger UI at `/docs`.

---

## 6. API Endpoints Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/v1/health` | Service health, providers, and supported languages |
| `GET` | `/api/v1/products/{id}/translations` | Get all language-specific content rows for a product |
| `GET` | `/api/v1/products/{id}/catalog?lang=hi` | Get localized catalog view with language fallback |
| `POST` | `/api/v1/products/{id}/translations` | Create or upsert a translation (`en`, `hi`, `mr`) |
| `PUT` | `/api/v1/products/{id}/translations/{lang}` | Update an existing translation |
| `POST` | `/api/v1/translate` | Translate product title and description into en, hi, mr |
| `POST` | `/api/v1/speech/transcribe` | Transcribe voice recording into text |

---

## 7. Database Migration

The file [`migrations/007_product_translations.sql`](file:///e:/Harsh/VIT/Hackathons/SIH%202026/Speech%20Translation/migrations/007_product_translations.sql) is fully idempotent and safe:
- Can be run directly in the Supabase SQL Editor.
- Contains NO destructive commands (`DROP`, `DELETE`, `TRUNCATE`).
- Applies Row Level Security (RLS) enforcing public visibility only on published products, and artisan editing ownership.
