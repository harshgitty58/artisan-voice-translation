# Artisan AI Copilot — Step-by-Step Components Implementation Guide
**Module:** Speech Translation & Multilingual Cataloging (SIH 2026)  
**Live Production URL:** `https://artisan-speech-translation.onrender.com`  
**Interactive Swagger Docs:** `https://artisan-speech-translation.onrender.com/docs`  
**Web Demo Studio:** `https://artisan-speech-translation.onrender.com/ui/`  

---

## 🏛️ System Architecture Overview

This module is split into **3 Core Backend Components** connected into an automated pipeline, plus a **Unified Web Studio Frontend**:

```
[Artisan Voice Audio]
         │
         ▼
┌──────────────────────────────────────────────────────────┐
│ COMPONENT 1: Voice & Language Onboarding Engine          │
│ • Google Cloud Speech-to-Text (hi-IN, mr-IN, en-IN)      │
│ • Automatic Spoken Language Detection                    │
│ • Heuristic Entity Extraction (Name, Material, Price)    │
└────────────────────────┬─────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────┐
│ COMPONENT 2: Artisan Knowledge Engine (3-Line Generator) │
│ • Craft Matching (Over 500+ Indian Artisanal Crafts)     │
│ • Line 1: Regional Origin & Historical Heritage          │
│ • Line 2: Authentic Material & Handloom/Craft Technique  │
│ • Line 3: Practical Utility, Ergonomics & Styling        │
└────────────────────────┬─────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────┐
│ COMPONENT 3: Tri-Lingual Translation & Table 007 DB      │
│ • Google Cloud Translation (English, Hindi, Marathi)     │
│ • "Translate-if-Missing" Cost-Saving Guard               │
│ • Supabase PostgreSQL `product_translations` (Table 007) │
│ • Localized Catalog Retrieval with English Fallback      │
└──────────────────────────────────────────────────────────┘
```

---

## Component 1: Voice & Language Onboarding Engine

### 1. Purpose
Empowers rural artisans who cannot easily type on smartphones to onboard products purely by speaking in their native dialect (**Hindi**, **Marathi**, or **English**).

### 2. Implementation Steps
1. **Audio Ingestion**: Accepts raw audio bytes (WebM, WAV, MP3, OGG) Base64-encoded from browser or mobile mic.
2. **Multi-Language Auto-STT**: Calls Google Cloud Speech-to-Text v1 with `alternativeLanguageCodes: ["hi-IN", "mr-IN", "en-IN"]`. The engine automatically detects which language was spoken without forcing the artisan to pick a language first.
3. **Information Extraction**:
   - Analyzes raw transcript using regex and linguistic rules.
   - Extracts `name_candidate` (e.g. *कोल्हापुरी चप्पल*), `material_hint` (e.g. *चमड़ा* / *leather*), and `price_hint` (e.g. *1000*).

### 3. Key Files
- `app/services/speech_service.py`
- `app/services/language_detection_service.py`
- `app/services/extraction_service.py`

### 4. API Usage
```http
POST /api/v1/speech/transcribe
Content-Type: application/json

{
  "audio_base64": "<BASE64_STRING>",
  "audio_encoding": "WEBM_OPUS",
  "language_code": "hi"
}
```

---

## Component 2: Artisan Knowledge Engine (3-Line Description Synthesizer)

### 1. Purpose
Artisans typically describe products simply (e.g., *"Kolhapuri chappal, pure leather, 1000 rs"*). This component transforms short artisan speech into a rich, compelling **3-line e-commerce story** that buyers love, without losing authenticity.

### 2. The 3-Line Structure
- **Line 1 (Heritage & GI Origin)**: Identifies the craft's geographic cluster, historical lineage, and centuries of cultural heritage (e.g., Peshwa era, Mughal court, or tribal roots).
- **Line 2 (Material & Craftsmanship)**: Highlights genuine materials (vegetable-tanned leather, Mulberry silk, river clay, brass) and meticulous handcrafting techniques.
- **Line 3 (Utility & Lifestyle)**: Describes how the product is used, its ergonomics, durability, and everyday or festive appeal.

### 3. Implementation Steps
1. **Product Entity Parsing**: Filters out numeric prices and informal chatter to capture the primary product identity (e.g., *"Kolhapuri chappal"*).
2. **Artisan Craft Knowledge Base**: Matches the item against a curated database of 500+ Indian artisanal crafts (spanning Kashmiri shawls, Paithani silk, Chanderi sarees, Terracotta pottery, Dhokra metalwork, Mojaris, and Blue Pottery).
3. **Template & Fallback Synthesis**: If a regional craft is recognized, it pulls verified historical data; if it's a unique custom item, it procedurally constructs the 3-line narrative around the detected material and utility.

### 4. Key Files
- `app/services/description_service.py`
- `datasets/generate_massive_hero_dataset.py`
- `datasets/artisan_rich_descriptions.csv`

### 5. API Usage
```http
POST /api/v1/description/generate
Content-Type: application/json

{
  "speech_input": "Kolhapuri chappal, pure leather, 1000 rs",
  "language": "en"
}
```

**Response Example:**
```json
{
  "english_description": "Originating from the historic artisan clusters of Kolhapur and Maharashtra, this handcrafted footwear embodies centuries of traditional cobbling heritage.\nConstructed from 100% genuine vegetable-tanned leather with hand-stitched detailing, offering natural breathability and a distinctive rustic finish.\nDesigned for comfortable everyday ethnic and casual wear, featuring a timeless open-toe silhouette that softens and molds to your feet over time.",
  "generation_source": "artisan_knowledge_synthesizer"
}
```

---

## Component 3: Tri-Lingual Translation & Table 007 Database Engine

### 1. Purpose
Enables hyper-local selling and national discovery by translating product details into **English (`en`)**, **Hindi (`hi`)**, and **Marathi (`mr`)**, and saving them in Supabase PostgreSQL under Table 007 (`public.product_translations`).

### 2. Implementation Steps
1. **Google Cloud Translation Integration**: Translates titles and descriptions reliably between Indian languages and English.
2. **Translate-if-Missing Guard**:
   - Before hitting Google APIs, the service checks if a translation already exists for that `product_id` and language in Supabase.
   - If a language row already exists with a valid name, that language is **skipped**, saving API costs and latency.
3. **Table 007 PostgreSQL Storage**:
   - Stores translations with a compound primary key / uniqueness constraint: `UNIQUE(product_id, language_code)`.
   - Prevents empty strings via database `CHECK` constraints.
4. **Localized Retrieval with English Fallback**:
   - When a buyer requests `/products/{id}/catalog?lang=mr`, if Marathi is missing, the service automatically falls back to English (or the primary available language) to ensure the storefront never breaks.

### 3. Key Files
- `app/services/translation_service.py`
- `app/services/supabase_service.py`
- `migrations/007_product_translations.sql`

### 4. API Usage
```http
POST /api/v1/translate
Content-Type: application/json

{
  "source_language": "en",
  "target_languages": ["en", "hi", "mr"],
  "name": "Kolhapuri Chappals",
  "description": "Originating from the historic artisan clusters of Kolhapur..."
}
```

---

## Component 4: Unified End-to-End Voice Cataloging Pipeline

### 1. Purpose
Chains all 3 components into **a single API call** for mobile and web apps.

```http
POST /api/v1/pipeline/voice-catalog
Content-Type: application/json

{
  "audio_base64": "<AUDIO_BASE64>",
  "audio_encoding": "WEBM_OPUS",
  "spoken_language": "hi",
  "product_id": "optional-uuid",
  "auto_store": false
}
```

### Execution Flow
1. Transcribes audio via **Component 1**.
2. Identifies language (`hi`, `mr`, `en`).
3. Extracts product details & material.
4. Generates rich 3-line description via **Component 2**.
5. Translates to all 3 languages via **Component 3**.
6. Returns complete draft to the artisan for review before publishing.

---

## How to Connect to Your Main Website

### 1. Frontend Integration (JavaScript / React / Next.js)
Call the live Render endpoint directly from your product form:
```javascript
const res = await fetch("https://artisan-speech-translation.onrender.com/api/v1/description/generate", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    speech_input: userInputText,
    language: "en"
  })
});
const { english_description } = await res.json();
```

### 2. Embed the Studio Portal (`<iframe>`)
```html
<iframe 
  src="https://artisan-speech-translation.onrender.com/ui/" 
  width="100%" 
  height="750px" 
  style="border: none; border-radius: 12px;"
  allow="microphone">
</iframe>
```
