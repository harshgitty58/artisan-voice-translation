import logging
from typing import Optional
import httpx
from app.core.config import settings
from app.schemas.translation import SpeechTranscribeResponse, SupportedLanguage

logger = logging.getLogger(__name__)

# BCP-47 language code mappings for Google Cloud Speech-to-Text
LANGUAGE_CODE_MAP = {
    SupportedLanguage.HINDI: "hi-IN",
    SupportedLanguage.MARATHI: "mr-IN",
    SupportedLanguage.ENGLISH: "en-IN",
}

GOOGLE_SPEECH_API_URL = "https://speech.googleapis.com/v1/speech:recognize"


class SpeechService:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.GOOGLE_CLOUD_API_KEY

    async def transcribe_audio(
        self,
        audio_content_base64: str,
        language: SupportedLanguage = SupportedLanguage.HINDI,
        encoding: str = "WEBM_OPUS",
        sample_rate_hertz: Optional[int] = None,
    ) -> SpeechTranscribeResponse:
        """
        Transcribe artisan audio input using Google Cloud Speech-to-Text REST API.
        If no API key is provided, provides an offline mock transcription for local testing.
        """
        lang_code = LANGUAGE_CODE_MAP.get(language, "hi-IN")

        if not self.api_key:
            logger.info("No GOOGLE_CLOUD_API_KEY provided. Using mock speech transcription.")
            return self._mock_transcription(language)

        payload = {
            "config": {
                "encoding": encoding,
                "languageCode": lang_code,
                "enableAutomaticPunctuation": True,
            },
            "audio": {
                "content": audio_content_base64
            }
        }

        if sample_rate_hertz:
            payload["config"]["sampleRateHertz"] = sample_rate_hertz

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{GOOGLE_SPEECH_API_URL}?key={self.api_key}",
                    json=payload,
                    headers={"Content-Type": "application/json"}
                )

                if response.status_code == 200:
                    data = response.json()
                    results = data.get("results", [])
                    if results:
                        best_alt = results[0]["alternatives"][0]
                        return SpeechTranscribeResponse(
                            transcript=best_alt.get("transcript", ""),
                            confidence=float(best_alt.get("confidence", 0.95)),
                            language_code=lang_code,
                            is_mock=False,
                        )
                    return SpeechTranscribeResponse(
                        transcript="",
                        confidence=0.0,
                        language_code=lang_code,
                        is_mock=False,
                    )
                else:
                    logger.warning(
                        f"Google Cloud Speech API responded with {response.status_code}: {response.text}. "
                        "Falling back to mock response."
                    )
                    return self._mock_transcription(language)

        except Exception as exc:
            logger.error(f"Error calling Google Cloud Speech API: {exc}. Falling back to mock transcription.")
            return self._mock_transcription(language)

    def _mock_transcription(self, language: SupportedLanguage) -> SpeechTranscribeResponse:
        mock_samples = {
            SupportedLanguage.HINDI: "यह हाथ से बना हुआ सुंदर सूती बैग है, प्राकृतिक रंगों से रंगा हुआ।",
            SupportedLanguage.MARATHI: "ही हातमागावर विणलेली अस्सल कापडी पिशवी आहे, नैसर्गिक रंगांचा वापर केला आहे.",
            SupportedLanguage.ENGLISH: "This is a handcrafted pure cotton bag dyed with organic natural colors.",
        }
        text = mock_samples.get(language, mock_samples[SupportedLanguage.HINDI])
        return SpeechTranscribeResponse(
            transcript=text,
            confidence=0.98,
            language_code=LANGUAGE_CODE_MAP.get(language, "hi-IN"),
            is_mock=True,
        )


speech_service = SpeechService()
