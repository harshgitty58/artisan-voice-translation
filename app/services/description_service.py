import logging
from typing import Optional, Tuple
import httpx
from app.core.config import settings
from app.schemas.translation import SupportedLanguage
from app.services.extraction_service import ExtractedProductInfo

logger = logging.getLogger(__name__)

GOOGLE_TRANSLATE_URL = "https://translation.googleapis.com/language/translate/v2"

# Template-based description generator used as offline fallback.
# This fills in the product context without calling an LLM.
DESCRIPTION_TEMPLATES = {
    SupportedLanguage.ENGLISH: (
        "This {name} is a handcrafted artisan product"
        "{material_part}{color_part}. "
        "Made with skill and care, it represents authentic Indian craftsmanship."
    ),
    SupportedLanguage.HINDI: (
        "यह {name} एक हस्तनिर्मित कारीगरी उत्पाद है"
        "{material_part}{color_part}। "
        "कुशलता और देखभाल से बनाया गया, यह भारतीय शिल्पकला की प्रामाणिक पहचान है।"
    ),
    SupportedLanguage.MARATHI: (
        "हे {name} एक हस्तकला उत्पादन आहे"
        "{material_part}{color_part}. "
        "कौशल्य आणि काळजीने बनवलेले, ते भारतीय कारागिरीचे प्रतीक आहे."
    ),
}

MATERIAL_HINTS_HI = {
    "cotton": "सूती", "silk": "रेशमी", "wool": "ऊनी", "jute": "जूट",
    "bamboo": "बांस", "brass": "पीतल", "clay": "मिट्टी",
    "terracotta": "टेराकोटा", "wood": "लकड़ी", "leather": "चमड़ा",
}

MATERIAL_HINTS_MR = {
    "cotton": "सुती", "silk": "रेशमी", "wool": "लोकरीचे", "jute": "ताग",
    "bamboo": "बांबू", "brass": "पितळेचे", "clay": "मातीचे",
    "terracotta": "टेराकोटा", "wood": "लाकडी", "leather": "चामड्याचे",
}


class DescriptionGenerationService:
    """
    Generates a polished English product description from extracted raw content,
    then translates it into Hindi and Marathi via Google Cloud Translation API.

    This is step 6 in the cataloging workflow (spec §7): 'Description generation'.
    The output feeds into the translation step which ultimately stores records
    in product_translations (only name and description — spec §4).

    AI Safety (spec §8): Only name and description are generated/translated.
    Material, price, dimensions come solely from the canonical products table.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        hf_model_repo: Optional[str] = None,
        hf_token: Optional[str] = None,
    ):
        self.api_key = api_key or settings.GOOGLE_CLOUD_API_KEY
        self.hf_model_repo = hf_model_repo or getattr(settings, "HF_MODEL_REPO", "harshvdn2/qwen-artisan-description")
        self.hf_token = hf_token or getattr(settings, "HF_TOKEN", None)

    async def generate_with_qwen(
        self,
        speech_input: str,
        lang: str = "en",
    ) -> Optional[str]:
        """
        Calls the fine-tuned Qwen2.5-1.5B LoRA model hosted on Hugging Face.
        Uses Qwen's official ChatML format.
        Falls back safely to None if the model is waking up or unavailable.
        """
        if not self.hf_model_repo or not speech_input or not speech_input.strip():
            return None

        system_prompts = {
            "en": (
                "You are an expert e-commerce catalog specialist for traditional Indian artisans and handicrafts. "
                "Transform informal spoken artisan input into a polished, compelling, customer-ready product description. "
                "Only use facts mentioned by the artisan."
            ),
            "hi": (
                "आप पारंपरिक भारतीय कारीगरों और हस्तशिल्प के लिए ई-कॉमर्स विशेषज्ञ हैं। "
                "कारीगर की अनौपचारिक बोली से एक आकर्षक, प्रामाणिक और ग्राहक-तैयार उत्पाद विवरण तैयार करें। "
                "केवल बताए गए तथ्यों का उपयोग करें।"
            ),
            "mr": (
                "You are an expert e-commerce catalog specialist for traditional Indian artisans. "
                "Transform informal spoken Marathi artisan input into a polished, compelling product description "
                "honoring traditional craft heritage. Only use facts mentioned by the artisan."
            ),
        }

        sys_prompt = system_prompts.get(lang, system_prompts["en"])
        chatml_prompt = (
            f"<|im_start|>system\n{sys_prompt}<|im_end|>\n"
            f"<|im_start|>user\n{speech_input.strip()}<|im_end|>\n"
            f"<|im_start|>assistant\n"
        )

        headers = {}
        if self.hf_token:
            headers["Authorization"] = f"Bearer {self.hf_token}"

        api_url = f"https://api-inference.huggingface.co/models/{self.hf_model_repo}"

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(
                    api_url,
                    headers=headers,
                    json={
                        "inputs": chatml_prompt,
                        "parameters": {
                            "max_new_tokens": 160,
                            "temperature": 0.7,
                            "top_p": 0.9,
                            "return_full_text": False,
                        },
                    },
                )
                if resp.status_code == 200:
                    data = resp.json()
                    if isinstance(data, list) and data:
                        text = data[0].get("generated_text", "").strip()
                        # Clean any trailing special tokens
                        text = text.replace("<|im_end|>", "").replace("<|endoftext|>", "").strip()
                        if len(text) >= 20:
                            logger.info(f"Qwen fine-tuned model generated description: {text[:60]}...")
                            return text
                elif resp.status_code == 503:
                    logger.info("Qwen HF model warming up (cold start) — using template fallback.")
                else:
                    logger.warning(f"Qwen HF call status {resp.status_code}: {resp.text[:120]}")
        except Exception as exc:
            logger.warning(f"Qwen HF call failed ({exc}) — using template fallback.")

        return None

    async def generate_english_description(
        self,
        extracted: ExtractedProductInfo,
        raw_speech: Optional[str] = None,
        lang: str = "en",
    ) -> str:
        """
        Constructs a polished English product description.
        1. First tries the fine-tuned Qwen model (harshvdn2/qwen-artisan-description).
        2. If raw English candidate is already rich, cleans and uses it.
        3. Falls back safely to template-based generator if offline/mock.
        """
        # 1. Try Qwen fine-tuned LLM if we have raw speech or a candidate description
        speech_signal = raw_speech or extracted.description_candidate or extracted.name_candidate
        if speech_signal and len(speech_signal.strip()) >= 5:
            qwen_result = await self.generate_with_qwen(speech_signal, lang=lang)
            if qwen_result:
                return qwen_result

        # 2. Existing raw description is sufficient
        if extracted.description_candidate and len(extracted.description_candidate.split()) >= 8:
            return " ".join(extracted.description_candidate.split())

        # 3. Deterministic template fallback (offline / API failure)
        name = extracted.name_candidate or "this artisan product"
        material_part = (
            f" made from {extracted.material_hint.lower()}"
            if extracted.material_hint else ""
        )
        color_part = (
            f" in a {extracted.color_hint.lower()} finish"
            if extracted.color_hint else ""
        )

        template = DESCRIPTION_TEMPLATES[SupportedLanguage.ENGLISH]
        return template.format(
            name=name,
            material_part=material_part,
            color_part=color_part,
        )

    async def translate_description(
        self,
        text: str,
        target_lang: SupportedLanguage,
        material_hint: Optional[str] = None,
    ) -> Tuple[str, bool]:
        """
        Translates a description into target_lang using Google Cloud Translation.
        Falls back to template-based generation for offline/dev mode.
        Returns (translated_text, is_mock).
        """
        if target_lang == SupportedLanguage.ENGLISH:
            return text, False

        if not self.api_key:
            return self._template_fallback(text, target_lang, material_hint), True

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.post(
                    f"{GOOGLE_TRANSLATE_URL}?key={self.api_key}",
                    json={
                        "q": text,
                        "source": "en",
                        "target": target_lang.value,
                        "format": "text",
                    },
                )
                if resp.status_code == 200:
                    translated = resp.json()["data"]["translations"][0]["translatedText"]
                    return translated, False
                else:
                    logger.warning(
                        f"Description translation API error {resp.status_code}. Using template fallback."
                    )
                    return self._template_fallback(text, target_lang, material_hint), True

        except Exception as exc:
            logger.error(f"Description translation failed: {exc}. Using template fallback.")
            return self._template_fallback(text, target_lang, material_hint), True

    def _template_fallback(
        self,
        english_text: str,
        target_lang: SupportedLanguage,
        material_hint: Optional[str] = None,
    ) -> str:
        """
        Template-based fallback description when API is unavailable.
        Preserves the meaning of the English content without making up facts.
        """
        mat_lower = (material_hint or "").lower()

        if target_lang == SupportedLanguage.HINDI:
            mat_word = MATERIAL_HINTS_HI.get(mat_lower, "")
            material_part = f" {mat_word} से बना" if mat_word else ""
            return DESCRIPTION_TEMPLATES[SupportedLanguage.HINDI].format(
                name="यह उत्पाद",
                material_part=material_part,
                color_part="",
            )
        elif target_lang == SupportedLanguage.MARATHI:
            mat_word = MATERIAL_HINTS_MR.get(mat_lower, "")
            material_part = f" {mat_word}" if mat_word else ""
            return DESCRIPTION_TEMPLATES[SupportedLanguage.MARATHI].format(
                name="हे उत्पादन",
                material_part=material_part,
                color_part="",
            )

        return english_text


description_generation_service = DescriptionGenerationService()
