import re
import logging
from dataclasses import dataclass
from typing import Optional
from app.schemas.translation import SupportedLanguage

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Regex patterns for structured field extraction from free-form artisan speech
# ---------------------------------------------------------------------------

# Common artisan product keywords across Hindi/Marathi/English
PRODUCT_NAME_SIGNALS = [
    # English
    r"(?:this is|it is|called|name(?:d)?(?:\s+is)?|product(?:\s+is)?)\s+[\"']?([A-Za-z\s]+(?:bag|pot|lamp|scarf|box|bowl|vase|mat|cloth|fabric|jewelry|jewellery|craft|art)[A-Za-z\s]*)[\"']?",
    # Captures noun phrases ending in known craft nouns
    r"\b([A-Za-z\s]*(?:handwoven|handmade|hand-?crafted|embroidered|carved|painted|woven|knitted|printed)[A-Za-z\s]*)\b",
]

PRICE_PATTERNS = [
    r"(?:price|cost|sell|selling)\s+(?:is\s+)?(?:₹|rs\.?|rupees?)\s*(\d+(?:,\d+)*)",
    r"(?:₹|rs\.?|rupees?)\s*(\d+(?:,\d+)*)",
    r"(\d+(?:,\d+)*)\s+(?:₹|rs\.?|rupees?)",
]

MATERIAL_SIGNALS = [
    r"\b(cotton|silk|wool|jute|bamboo|brass|copper|clay|terracotta|wood(?:en)?|cane|leather|linen)\b",
]

COLOR_SIGNALS = [
    r"\b(red|blue|green|yellow|orange|purple|black|white|brown|pink|indigo|violet|golden|silver|natural)\b",
]


@dataclass
class ExtractedProductInfo:
    """
    Structured product information extracted from artisan's transcribed speech.
    Only name and description are intended for product_translations table (§3).
    Other fields (material, price) are for the canonical products table — extracted
    here to inform the description generation step, NOT stored in product_translations.
    """
    raw_transcript: str
    detected_language: SupportedLanguage
    name_candidate: Optional[str] = None
    description_candidate: Optional[str] = None
    material_hint: Optional[str] = None
    color_hint: Optional[str] = None
    price_hint: Optional[int] = None
    extraction_confidence: float = 0.0
    is_mock: bool = False


class ProductExtractionService:
    """
    Parses structured product information from raw artisan speech transcripts.
    This is step 4 in the cataloging workflow (spec §7): 'Product information extraction'.

    Important: This service ONLY extracts candidates for name and description
    (the fields belonging to product_translations). Material, price, dimensions
    are extracted as hints to guide description generation — they must be
    validated and stored separately in the products canonical table.
    """

    def extract(
        self,
        transcript: str,
        detected_language: SupportedLanguage,
    ) -> ExtractedProductInfo:
        """
        Extracts candidate product name and description from artisan's transcribed speech.
        Uses regex patterns for English input; applies heuristic chunking for Hindi/Marathi.
        """
        result = ExtractedProductInfo(
            raw_transcript=transcript,
            detected_language=detected_language,
        )

        if not transcript or not transcript.strip():
            result.is_mock = True
            return result

        if detected_language == SupportedLanguage.ENGLISH:
            return self._extract_english(transcript, result)
        else:
            return self._extract_indic(transcript, result)

    def _extract_english(self, text: str, result: ExtractedProductInfo) -> ExtractedProductInfo:
        lower = text.lower()

        # Attempt name extraction
        for pattern in PRODUCT_NAME_SIGNALS:
            match = re.search(pattern, lower, re.IGNORECASE)
            if match:
                result.name_candidate = match.group(1).strip().title()
                result.extraction_confidence = 0.75
                break

        # Material hint (for description generation, not for product_translations)
        for pattern in MATERIAL_SIGNALS:
            match = re.search(pattern, lower, re.IGNORECASE)
            if match:
                result.material_hint = match.group(1).strip().capitalize()
                break

        # Color hint
        for pattern in COLOR_SIGNALS:
            match = re.search(pattern, lower, re.IGNORECASE)
            if match:
                result.color_hint = match.group(1).strip().capitalize()
                break

        # Price hint
        for pattern in PRICE_PATTERNS:
            match = re.search(pattern, lower, re.IGNORECASE)
            if match:
                try:
                    result.price_hint = int(match.group(1).replace(",", ""))
                except ValueError:
                    pass
                break

        # Use full transcript as description candidate if not too long
        cleaned = re.sub(r"\s+", " ", text).strip()
        result.description_candidate = cleaned if len(cleaned) <= 500 else cleaned[:500] + "..."

        # Fallback name from first 5 meaningful words
        if not result.name_candidate:
            words = [w for w in cleaned.split() if len(w) > 2][:5]
            if words:
                result.name_candidate = " ".join(words).title()
                result.extraction_confidence = 0.4

        return result

    def _extract_indic(self, text: str, result: ExtractedProductInfo) -> ExtractedProductInfo:
        """
        For Hindi/Marathi transcripts: use heuristic sentence chunking.
        The first meaningful sentence is the name candidate; full text is description candidate.
        """
        # Split on common sentence-ending punctuation (Devanagari danda |, . etc.)
        sentences = re.split(r"[।\.\!\?]", text.strip())
        sentences = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 3]

        if sentences:
            result.name_candidate = sentences[0][:80]  # cap at 80 chars for a product name
            result.extraction_confidence = 0.6

        result.description_candidate = text.strip()
        result.is_mock = False
        return result


product_extraction_service = ProductExtractionService()
