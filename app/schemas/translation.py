from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, field_validator


class SupportedLanguage(str, Enum):
    ENGLISH = "en"
    HINDI = "hi"
    MARATHI = "mr"


def validate_non_empty_string(v: Optional[str]) -> Optional[str]:
    if v is not None:
        stripped = v.strip()
        if not stripped:
            raise ValueError("Field cannot be an empty or whitespace-only string")
        return stripped
    return v


class TranslationBase(BaseModel):
    name: Optional[str] = Field(None, description="Translated product name")
    description: Optional[str] = Field(None, description="Translated product narrative / description")

    @field_validator("name", "description")
    @classmethod
    def check_non_empty(cls, v: Optional[str]) -> Optional[str]:
        return validate_non_empty_string(v)


class TranslationCreateRequest(TranslationBase):
    language_code: SupportedLanguage = Field(
        ..., 
        description="Target language code: en (English), hi (Hindi), or mr (Marathi)"
    )


class TranslationUpdateRequest(TranslationBase):
    pass


class TranslationResponse(TranslationBase):
    id: UUID = Field(default_factory=uuid4)
    product_id: UUID
    language_code: SupportedLanguage
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = {
        "from_attributes": True
    }


class ProductMultilingualCatalogResponse(BaseModel):
    product_id: UUID
    requested_language: SupportedLanguage
    resolved_language: SupportedLanguage
    is_fallback: bool
    name: str
    description: Optional[str] = None
    available_languages: List[SupportedLanguage]
    translations: Dict[str, TranslationResponse]


class SpeechTranscribeRequest(BaseModel):
    audio_base64: str = Field(..., description="Base64 encoded audio recording of the artisan")
    language_code: SupportedLanguage = Field(
        SupportedLanguage.HINDI,
        description="Spoken language code (hi, mr, en)"
    )
    audio_encoding: str = Field("WEBM_OPUS", description="Audio encoding: WEBM_OPUS, MP3, LINEAR16, etc.")
    sample_rate_hertz: Optional[int] = Field(None, description="Sample rate in Hertz")


class SpeechTranscribeResponse(BaseModel):
    transcript: str
    confidence: float
    language_code: str
    is_mock: bool = False


class TranslateCatalogRequest(BaseModel):
    product_id: Optional[UUID] = None
    source_language: SupportedLanguage = Field(
        SupportedLanguage.ENGLISH, 
        description="Language of the input name/description"
    )
    target_languages: List[SupportedLanguage] = Field(
        default_factory=lambda: [
            SupportedLanguage.ENGLISH, 
            SupportedLanguage.HINDI, 
            SupportedLanguage.MARATHI
        ],
        description="Languages to generate translations for"
    )
    name: str = Field(..., min_length=1, description="Source product title")
    description: Optional[str] = Field(None, description="Source product description")

    @field_validator("name", "description")
    @classmethod
    def check_non_empty(cls, v: Optional[str]) -> Optional[str]:
        return validate_non_empty_string(v)


class TranslatedItem(BaseModel):
    language_code: SupportedLanguage
    name: str
    description: Optional[str] = None


class TranslateCatalogResponse(BaseModel):
    product_id: Optional[UUID] = None
    source_language: SupportedLanguage
    translations: List[TranslatedItem]
    is_mock: bool = False
    skipped_languages: List[SupportedLanguage] = Field(
        default_factory=list,
        description="Languages skipped because a valid stored translation already existed (translate-if-missing)"
    )


# ---------------------------------------------------------------------------
# Pipeline Step Schemas — Full cataloging workflow (spec §7)
# ---------------------------------------------------------------------------

class LanguageDetectRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Text to detect language from")


class LanguageDetectResponse(BaseModel):
    detected_language: SupportedLanguage
    confidence: float
    is_mock: bool = False


class VoicePipelineRequest(BaseModel):
    """
    Full voice cataloging pipeline request (spec §7).
    Steps: speech-to-text → language detection → extraction → description generation → translation.
    Only name and description are stored in product_translations (spec §4).
    """
    audio_base64: str = Field(..., description="Base64 encoded audio from artisan")
    audio_encoding: str = Field("WEBM_OPUS", description="Audio encoding format")
    sample_rate_hertz: Optional[int] = None
    spoken_language: SupportedLanguage = Field(
        SupportedLanguage.HINDI,
        description="Language the artisan spoke in"
    )
    product_id: Optional[UUID] = Field(
        None,
        description="If provided, translations will be stored to this product (translate-if-missing applies)"
    )
    auto_store: bool = Field(
        False,
        description="If true and product_id is given, store translations automatically after generation"
    )


class ExtractedProductDraft(BaseModel):
    """
    Represents the structured product information extracted from artisan speech.
    name and description are candidates for product_translations.
    material_hint, price_hint, color_hint are informational — they belong to products table.
    """
    name_candidate: Optional[str] = None
    description_candidate: Optional[str] = None
    material_hint: Optional[str] = Field(None, description="Informational — store in products, not product_translations")
    color_hint: Optional[str] = Field(None, description="Informational — store in products, not product_translations")
    price_hint: Optional[int] = Field(None, description="Informational — store in products, not product_translations")
    extraction_confidence: float = 0.0


class VoicePipelineResponse(BaseModel):
    """Full pipeline result returned to client for artisan review/edit before final storage."""
    transcript: str
    transcript_confidence: float
    detected_language: SupportedLanguage
    language_confidence: float
    extracted_draft: ExtractedProductDraft
    generated_translations: TranslateCatalogResponse
    stored: bool = False
    skipped_languages: List[SupportedLanguage] = Field(default_factory=list)
    is_mock: bool = False


class DescriptionGenerateRequest(BaseModel):
    """Direct request to test artisan description generation."""
    speech_input: str = Field(..., min_length=3, description="Informal artisan speech or product notes")
    language: SupportedLanguage = Field(SupportedLanguage.HINDI, description="Input language (en, hi, mr)")


class DescriptionGenerateResponse(BaseModel):
    """Result of description generation."""
    input_text: str
    language: SupportedLanguage
    english_description: str
    generation_source: str = Field(..., description="Method used: qwen_lora, google_translate_pipeline, or template_fallback")


