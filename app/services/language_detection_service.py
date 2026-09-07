import logging
from typing import Dict, Optional, Tuple
import httpx
from app.core.config import settings
from app.schemas.translation import SupportedLanguage

logger = logging.getLogger(__name__)

GOOGLE_LANGUAGE_DETECT_URL = "https://translation.googleapis.com/language/translate/v2/detect"

# BCP-47 → SupportedLanguage mapping (MVP subset only)
DETECT_CODE_MAP: Dict[str, SupportedLanguage] = {
    "en": SupportedLanguage.ENGLISH,
    "hi": SupportedLanguage.HINDI,
    "mr": SupportedLanguage.MARATHI,
}


class LanguageDetectionService:
    """
    Detects the language of a text string using Google Cloud Translation API's
    language detection endpoint. This step sits between speech-to-text and
    product information extraction in the cataloging workflow (spec §7).
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.GOOGLE_CLOUD_API_KEY

    async def detect(self, text: str) -> Tuple[SupportedLanguage, float, bool]:
        """
        Detect the language of the given text.
        Returns: (SupportedLanguage, confidence: float, is_mock: bool)
        Falls back to Hindi if the detected language is outside the MVP set,
        since most artisan voice content is expected to be in Hindi or Marathi.
        """
        if not text or not text.strip():
            return SupportedLanguage.HINDI, 0.0, True

        if not self.api_key:
            return self._mock_detect(text)

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(
                    f"{GOOGLE_LANGUAGE_DETECT_URL}?key={self.api_key}",
                    json={"q": text},
                    headers={"Content-Type": "application/json"},
                )

                if resp.status_code == 200:
                    data = resp.json()
                    detections = data.get("data", {}).get("detections", [[]])[0]
                    if detections:
                        best = detections[0]
                        detected_code = best.get("language", "hi")
                        confidence = float(best.get("confidence", 0.9))

                        # Map to supported language; default to Hindi if unsupported
                        lang = DETECT_CODE_MAP.get(detected_code, SupportedLanguage.HINDI)
                        if detected_code not in DETECT_CODE_MAP:
                            logger.warning(
                                f"Detected language '{detected_code}' is outside MVP set. "
                                f"Defaulting to Hindi."
                            )
                        return lang, confidence, False

                logger.warning(
                    f"Language detect API returned {resp.status_code}. Using mock fallback."
                )
                return self._mock_detect(text)

        except Exception as exc:
            logger.error(f"Language detection failed: {exc}. Using mock fallback.")
            return self._mock_detect(text)

    def _mock_detect(self, text: str) -> Tuple[SupportedLanguage, float, bool]:
        """
        Heuristic offline language detection for development.
        Checks for Devanagari Unicode block characters to distinguish
        Hindi/Marathi from English.
        """
        devanagari_chars = sum(
            1 for c in text if "\u0900" <= c <= "\u097F"
        )
        ratio = devanagari_chars / max(len(text.strip()), 1)

        if ratio > 0.3:
            # Marathi heuristic: contains common Marathi-only characters/endings
            marathi_markers = ["आहे", "केले", "विणलेली", "पिशवी", "मातीचे", "पितळेचा"]
            if any(marker in text for marker in marathi_markers):
                return SupportedLanguage.MARATHI, 0.82, True
            return SupportedLanguage.HINDI, 0.85, True

        return SupportedLanguage.ENGLISH, 0.95, True


language_detection_service = LanguageDetectionService()
