from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, HTTPException, Query, status

from app.core.config import settings
from app.schemas.translation import (
    DescriptionGenerateRequest,
    DescriptionGenerateResponse,
    ExtractedProductDraft,
    LanguageDetectRequest,
    LanguageDetectResponse,
    ProductMultilingualCatalogResponse,
    SpeechTranscribeRequest,
    SpeechTranscribeResponse,
    SupportedLanguage,
    TranslateCatalogRequest,
    TranslateCatalogResponse,
    TranslationCreateRequest,
    TranslationResponse,
    TranslationUpdateRequest,
    VoicePipelineRequest,
    VoicePipelineResponse,
)
from app.services.description_service import description_generation_service
from app.services.extraction_service import product_extraction_service
from app.services.language_detection_service import language_detection_service
from app.services.speech_service import speech_service
from app.services.supabase_service import translation_repo
from app.services.translation_service import translation_service

router = APIRouter()


# ===========================================================================
# Health
# ===========================================================================

@router.get("/health", tags=["Health"])
async def health_check():
    """Service health and capability verification."""
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "environment": settings.ENVIRONMENT,
        "google_cloud_configured": bool(settings.GOOGLE_CLOUD_API_KEY),
        "supabase_configured": bool(
            settings.SUPABASE_URL
            and "your-project" not in settings.SUPABASE_URL
        ),
        "supported_languages": [lang.value for lang in SupportedLanguage],
        "pipeline_steps": [
            "speech-to-text",
            "language-detection",
            "product-extraction",
            "description-generation",
            "translation",
            "store",
        ],
    }


# ===========================================================================
# Product Translations CRUD (Table 007)
# ===========================================================================

@router.get(
    "/products/{product_id}/translations",
    response_model=List[TranslationResponse],
    tags=["Product Translations"],
    summary="Get all translations for a product",
)
async def list_product_translations(product_id: UUID):
    """
    Retrieve all language-specific content rows for a canonical product (Table 007).
    Returns an empty list while the product is still in draft.
    """
    return await translation_repo.get_translations_for_product(product_id)


@router.get(
    "/products/{product_id}/catalog",
    response_model=ProductMultilingualCatalogResponse,
    tags=["Product Translations"],
    summary="Get localized catalog view with fallback (spec §18)",
)
async def get_localized_product_catalog(
    product_id: UUID,
    lang: SupportedLanguage = Query(
        SupportedLanguage.ENGLISH,
        description="Preferred language (en, hi, mr)"
    ),
):
    """
    Retrieve localized product name and description.
    If the requested language translation does not exist, falls back to English
    or the first available language (spec §18 language fallback policy).
    """
    all_translations = await translation_repo.get_translations_for_product(product_id)
    trans_map = {t.language_code: t for t in all_translations}

    if not trans_map:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No translations found for product {product_id}",
        )

    is_fallback = False
    resolved_lang = lang
    target = trans_map.get(lang)

    if not target or not target.name:
        is_fallback = True
        if SupportedLanguage.ENGLISH in trans_map and trans_map[SupportedLanguage.ENGLISH].name:
            target = trans_map[SupportedLanguage.ENGLISH]
            resolved_lang = SupportedLanguage.ENGLISH
        else:
            resolved_lang, target = next(iter(trans_map.items()))

    return ProductMultilingualCatalogResponse(
        product_id=product_id,
        requested_language=lang,
        resolved_language=resolved_lang,
        is_fallback=is_fallback,
        name=target.name or "Untitled Product",
        description=target.description,
        available_languages=list(trans_map.keys()),
        translations={k.value: v for k, v in trans_map.items()},
    )


@router.post(
    "/products/{product_id}/translations",
    response_model=TranslationResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Product Translations"],
    summary="Create or update a product translation",
)
async def upsert_product_translation(
    product_id: UUID,
    payload: TranslationCreateRequest,
):
    """
    Store or update an artisan-reviewed translation for a product.
    Enforces uniqueness of (product_id, language_code) and rejects empty strings.
    """
    return await translation_repo.upsert_translation(
        product_id=product_id,
        language_code=payload.language_code,
        name=payload.name,
        description=payload.description,
    )


@router.put(
    "/products/{product_id}/translations/{language_code}",
    response_model=TranslationResponse,
    tags=["Product Translations"],
    summary="Update an existing translation after artisan review/edit",
)
async def update_product_translation(
    product_id: UUID,
    language_code: SupportedLanguage,
    payload: TranslationUpdateRequest,
):
    """
    Update an existing translation after artisan review or editing (spec §8 — AI safety).
    """
    return await translation_repo.upsert_translation(
        product_id=product_id,
        language_code=language_code,
        name=payload.name,
        description=payload.description,
    )


# ===========================================================================
# Translation Engine
# ===========================================================================

@router.post(
    "/translate",
    response_model=TranslateCatalogResponse,
    tags=["Translation Engine"],
    summary="Generate multilingual translations with translate-if-missing guard (spec §16)",
)
async def generate_translations(payload: TranslateCatalogRequest):
    """
    Translates canonical product title and description into en, hi, mr using
    Google Cloud Translation API.

    translate-if-missing guard (spec §16):
    If product_id is provided, checks existing stored translations first.
    Languages that already have a valid stored name are SKIPPED — no repeated API calls.
    """
    existing_languages: List[SupportedLanguage] = []

    if payload.product_id:
        existing = await translation_repo.get_translations_for_product(payload.product_id)
        # Only consider a language "existing" if it has a non-empty name stored
        existing_languages = [
            t.language_code for t in existing if t.name and t.name.strip()
        ]

    return await translation_service.generate_catalog_translations(
        payload,
        existing_languages=existing_languages,
    )


# ===========================================================================
# Speech Engine — Step 1 & 2 of Pipeline
# ===========================================================================

@router.post(
    "/speech/transcribe",
    response_model=SpeechTranscribeResponse,
    tags=["Speech Engine"],
    summary="Step 1: Transcribe artisan voice input via Google Cloud Speech-to-Text (spec §7)",
)
async def transcribe_speech(payload: SpeechTranscribeRequest):
    """
    Processes artisan voice audio in Hindi (hi-IN), Marathi (mr-IN), or English (en-IN).
    Uses Google Cloud Speech-to-Text REST API.
    """
    return await speech_service.transcribe_audio(
        audio_content_base64=payload.audio_base64,
        language=payload.language_code,
        encoding=payload.audio_encoding,
        sample_rate_hertz=payload.sample_rate_hertz,
    )


@router.post(
    "/speech/detect-language",
    response_model=LanguageDetectResponse,
    tags=["Speech Engine"],
    summary="Step 2: Detect language of transcribed text (spec §7)",
)
async def detect_language(payload: LanguageDetectRequest):
    """
    Detects the spoken language from transcribed text.
    Supports en, hi, mr. Unsupported detected languages default to Hindi.
    Uses Google Cloud Translation detect endpoint or Devanagari heuristic fallback.
    """
    lang, confidence, is_mock = await language_detection_service.detect(payload.text)
    return LanguageDetectResponse(
        detected_language=lang,
        confidence=confidence,
        is_mock=is_mock,
    )


# ===========================================================================
# Full Voice Cataloging Pipeline — All 7 steps in one call
# ===========================================================================

@router.post(
    "/pipeline/voice-catalog",
    response_model=VoicePipelineResponse,
    tags=["Voice Pipeline"],
    summary="Full voice cataloging pipeline: speech → detect → extract → describe → translate (spec §7)",
)
async def run_voice_catalog_pipeline(payload: VoicePipelineRequest):
    """
    Executes the complete artisan cataloging workflow from raw audio to multilingual draft:

    1. Speech-to-Text       → Google Cloud Speech-to-Text
    2. Language Detection   → Google Cloud Translation detect (or Devanagari heuristic)
    3. Product Extraction   → Regex/heuristic parser extracts name/description candidates
    4. Description Gen      → Polishes raw extracted text into a clean English description
    5. Translation          → Translate into en, hi, mr (translate-if-missing guard applied)
    6. (Optional) Store     → If auto_store=True and product_id given, stores to product_translations

    The response is returned to the artisan for review/edit before finalizing (spec §8 AI safety).
    Only name and description are eligible for product_translations (spec §4).
    """
    # Step 1: Speech-to-Text
    speech_result = await speech_service.transcribe_audio(
        audio_content_base64=payload.audio_base64,
        language=payload.spoken_language,
        encoding=payload.audio_encoding,
        sample_rate_hertz=payload.sample_rate_hertz,
    )
    transcript = speech_result.transcript

    # Step 2: Language Detection
    detected_lang, lang_confidence, lang_is_mock = await language_detection_service.detect(transcript)

    # Step 3: Product Information Extraction
    extracted = product_extraction_service.extract(transcript, detected_lang)

    # Step 4: Description Generation (Fine-Tuned Qwen LLM with Template Fallback)
    english_description = await description_generation_service.generate_english_description(
        extracted,
        raw_speech=transcript,
        lang=detected_lang.value if hasattr(detected_lang, "value") else str(detected_lang),
    )

    # Step 5: Translation with translate-if-missing guard
    existing_languages: List[SupportedLanguage] = []
    if payload.product_id:
        stored = await translation_repo.get_translations_for_product(payload.product_id)
        existing_languages = [t.language_code for t in stored if t.name and t.name.strip()]

    translate_request = TranslateCatalogRequest(
        product_id=payload.product_id,
        # Use the actual detected language as source so the translation service
        # knows what language it is translating FROM (fixes EN→EN short-circuit bug).
        source_language=detected_lang,
        target_languages=[SupportedLanguage.ENGLISH, SupportedLanguage.HINDI, SupportedLanguage.MARATHI],
        name=extracted.name_candidate or transcript[:80],
        description=english_description,
    )

    translation_result = await translation_service.generate_catalog_translations(
        translate_request,
        existing_languages=existing_languages,
    )

    # Step 6: (Optional) Auto-store to product_translations
    stored_flag = False
    if payload.auto_store and payload.product_id and translation_result.translations:
        for item in translation_result.translations:
            await translation_repo.upsert_translation(
                product_id=payload.product_id,
                language_code=item.language_code,
                name=item.name,
                description=item.description,
            )
        stored_flag = True

    return VoicePipelineResponse(
        transcript=transcript,
        transcript_confidence=speech_result.confidence,
        detected_language=detected_lang,
        language_confidence=lang_confidence,
        extracted_draft=ExtractedProductDraft(
            name_candidate=extracted.name_candidate,
            description_candidate=extracted.description_candidate,
            material_hint=extracted.material_hint,
            color_hint=extracted.color_hint,
            price_hint=extracted.price_hint,
            extraction_confidence=extracted.extraction_confidence,
        ),
        generated_translations=translation_result,
        stored=stored_flag,
        skipped_languages=translation_result.skipped_languages,
        is_mock=speech_result.is_mock or lang_is_mock or translation_result.is_mock,
    )


# ===========================================================================
# Dedicated Description Generator (Qwen2.5 LoRA & Fallback)
# ===========================================================================

@router.post(
    "/description/generate",
    response_model=DescriptionGenerateResponse,
    tags=["Description Generator"],
    summary="Generate customer-ready English artisan catalog description",
)
async def generate_artisan_description(payload: DescriptionGenerateRequest):
    """
    Transforms informal artisan speech/notes into a polished English product description.
    Uses Fine-Tuned Qwen2.5 LoRA model, with automatic fallback to Google Cloud Translation.
    """
    desc, source = await description_generation_service.generate_with_details(
        speech_input=payload.speech_input,
        lang=payload.language.value,
    )
    return DescriptionGenerateResponse(
        input_text=payload.speech_input,
        language=payload.language,
        english_description=desc,
        generation_source=source,
    )

