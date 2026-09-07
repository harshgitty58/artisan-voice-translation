import logging
from typing import Dict, List, Optional, Tuple
import httpx
from app.core.config import settings
from app.schemas.translation import (
    SupportedLanguage,
    TranslateCatalogRequest,
    TranslateCatalogResponse,
    TranslatedItem,
)

logger = logging.getLogger(__name__)

GOOGLE_TRANSLATE_API_URL = "https://translation.googleapis.com/language/translate/v2"

# Curated artisan domain dictionary for high-fidelity offline translation fallback
ARTISAN_DICTIONARY: Dict[str, Dict[SupportedLanguage, str]] = {
    "handwoven cotton bag": {
        SupportedLanguage.ENGLISH: "Handwoven Cotton Bag",
        SupportedLanguage.HINDI: "हाथ से बुना सूती बैग",
        SupportedLanguage.MARATHI: "हातमागावर विणलेली कापडी पिशवी",
    },
    "terracotta clay pot": {
        SupportedLanguage.ENGLISH: "Terracotta Clay Pot",
        SupportedLanguage.HINDI: "टेराकोटा मिट्टी का बर्तन",
        SupportedLanguage.MARATHI: "टेराकोटा मातीचे भांडे",
    },
    "brass decorative lamp": {
        SupportedLanguage.ENGLISH: "Brass Decorative Lamp",
        SupportedLanguage.HINDI: "पीतल का सजावटी दीया",
        SupportedLanguage.MARATHI: "पितळेचा शोभिवंत दिवा",
    },
    "embroidered silk scarf": {
        SupportedLanguage.ENGLISH: "Embroidered Silk Scarf",
        SupportedLanguage.HINDI: "कढ़ाईदार रेशमी दुपट्टा",
        SupportedLanguage.MARATHI: "कशीदाकारी केलेले रेशमी स्कार्फ",
    },
    "wooden carved jewelry box": {
        SupportedLanguage.ENGLISH: "Wooden Carved Jewelry Box",
        SupportedLanguage.HINDI: "नक्काशीदार लकड़ी का आभूषण डिब्बा",
        SupportedLanguage.MARATHI: "लाकडी नक्षीकाम केलेले दागिन्यांचे पेटी",
    },
}


class TranslationService:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.GOOGLE_CLOUD_API_KEY

    async def translate_text(
        self,
        text: str,
        target_lang: SupportedLanguage,
        source_lang: Optional[SupportedLanguage] = None,
    ) -> Tuple[str, bool]:
        """
        Translates a single string into the target language using Google Cloud Translation API.
        Returns: (translated_text, is_mock)
        """
        if not text or not text.strip():
            return text, False

        # If source and target are the same, return as is
        if source_lang and source_lang == target_lang:
            return text, False

        if not self.api_key:
            return self._mock_translate_phrase(text, target_lang), True

        try:
            payload = {
                "q": text,
                "target": target_lang.value,
                "format": "text",
            }
            if source_lang:
                payload["source"] = source_lang.value

            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.post(
                    f"{GOOGLE_TRANSLATE_API_URL}?key={self.api_key}",
                    json=payload,
                )

                if resp.status_code == 200:
                    data = resp.json()
                    translated = data["data"]["translations"][0]["translatedText"]
                    return translated, False
                else:
                    logger.warning(
                        f"Google Translation API error ({resp.status_code}): {resp.text}. Using mock fallback."
                    )
                    return self._mock_translate_phrase(text, target_lang), True

        except Exception as exc:
            logger.error(f"Translation request failed: {exc}. Using mock fallback.")
            return self._mock_translate_phrase(text, target_lang), True

    async def generate_catalog_translations(
        self,
        request: TranslateCatalogRequest,
        existing_languages: Optional[List[SupportedLanguage]] = None,
    ) -> TranslateCatalogResponse:
        """
        Generates product translations across requested target languages (English, Hindi, Marathi).
        Guarantees that factual non-text fields are untouched (spec §8).

        translate-if-missing guard (spec §16):
            If existing_languages is provided (fetched from product_translations DB),
            any language already stored with a non-empty name is SKIPPED to avoid
            unnecessary API calls and re-generation costs.
        """
        translated_items: List[TranslatedItem] = []
        skipped: List[SupportedLanguage] = []
        is_any_mock = False
        existing_set = set(existing_languages or [])

        for target_lang in request.target_languages:
            # Translate-if-missing: skip this language if already stored
            if target_lang in existing_set:
                skipped.append(target_lang)
                continue

            if target_lang == request.source_language:
                translated_items.append(
                    TranslatedItem(
                        language_code=target_lang,
                        name=request.name,
                        description=request.description,
                    )
                )
                continue

            trans_name, mock_n = await self.translate_text(
                request.name,
                target_lang=target_lang,
                source_lang=request.source_language,
            )

            trans_desc = None
            mock_d = False
            if request.description:
                trans_desc, mock_d = await self.translate_text(
                    request.description,
                    target_lang=target_lang,
                    source_lang=request.source_language,
                )

            if mock_n or mock_d:
                is_any_mock = True

            translated_items.append(
                TranslatedItem(
                    language_code=target_lang,
                    name=trans_name,
                    description=trans_desc,
                )
            )

        return TranslateCatalogResponse(
            product_id=request.product_id,
            source_language=request.source_language,
            translations=translated_items,
            skipped_languages=skipped,
            is_mock=is_any_mock or (self.api_key is None),
        )

    def _mock_translate_phrase(self, text: str, target_lang: SupportedLanguage) -> str:
        """
        Smart fallback translator for demo & offline testing when API key is not configured.
        """
        lower = text.strip().lower()
        if lower in ARTISAN_DICTIONARY and target_lang in ARTISAN_DICTIONARY[lower]:
            return ARTISAN_DICTIONARY[lower][target_lang]

        # General contextual mock prefixes/suffixes if text is descriptive
        if target_lang == SupportedLanguage.HINDI:
            return f"[हिंदी] {text}"
        elif target_lang == SupportedLanguage.MARATHI:
            return f"[मराठी] {text}"
        return text


translation_service = TranslationService()
