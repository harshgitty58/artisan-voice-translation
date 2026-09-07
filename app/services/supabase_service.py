import logging
from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID, uuid4
from app.core.config import settings
from app.schemas.translation import (
    SupportedLanguage,
    TranslationResponse,
)

logger = logging.getLogger(__name__)


class SupabaseTranslationRepository:
    def __init__(self):
        self.supabase_client = None
        self._in_memory_store: Dict[str, Dict[str, dict]] = {}  # product_id -> {lang: dict}

        # Seed with initial sample products for offline testing
        self._seed_sample_data()

        if settings.SUPABASE_URL and settings.SUPABASE_ANON_KEY and "your-project" not in settings.SUPABASE_URL:
            try:
                from supabase import create_client
                key = settings.SUPABASE_SERVICE_ROLE_KEY or settings.SUPABASE_ANON_KEY
                self.supabase_client = create_client(settings.SUPABASE_URL, key)
                logger.info("Connected to Supabase client successfully.")
            except Exception as e:
                logger.warning(f"Could not initialize Supabase client: {e}. Falling back to in-memory store.")

    def _seed_sample_data(self):
        sample_id = "00000000-0000-0000-0000-000000000001"
        self._in_memory_store[sample_id] = {
            "en": {
                "id": uuid4(),
                "product_id": UUID(sample_id),
                "language_code": SupportedLanguage.ENGLISH,
                "name": "Handwoven Cotton Bag",
                "description": "Pure cotton reusable tote bag handwoven by master artisans in Maharashtra.",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            },
            "hi": {
                "id": uuid4(),
                "product_id": UUID(sample_id),
                "language_code": SupportedLanguage.HINDI,
                "name": "हाथ से बुना सूती बैग",
                "description": "महाराष्ट्र के कुशल कारीगरों द्वारा हाथ से बुना गया शुद्ध सूती दोबारा इस्तेमाल होने वाला टोट बैग।",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            },
            "mr": {
                "id": uuid4(),
                "product_id": UUID(sample_id),
                "language_code": SupportedLanguage.MARATHI,
                "name": "हातमागावर विणलेली कापडी पिशवी",
                "description": "महाराष्ट्रातील कुशल कारागिरांनी हातमागावर विणलेली शुद्ध सुती पिशवी.",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            },
        }

    async def get_translations_for_product(self, product_id: UUID) -> List[TranslationResponse]:
        pid_str = str(product_id)
        if self.supabase_client:
            try:
                response = self.supabase_client.table("product_translations") \
                    .select("*") \
                    .eq("product_id", pid_str) \
                    .execute()
                return [TranslationResponse(**item) for item in response.data]
            except Exception as e:
                logger.error(f"Error fetching translations from Supabase: {e}. Checking in-memory store.")

        # In-memory fallback
        product_dict = self._in_memory_store.get(pid_str, {})
        return [TranslationResponse(**v) for v in product_dict.values()]

    async def get_translation_by_language(
        self, product_id: UUID, language_code: SupportedLanguage
    ) -> Optional[TranslationResponse]:
        pid_str = str(product_id)
        if self.supabase_client:
            try:
                response = self.supabase_client.table("product_translations") \
                    .select("*") \
                    .eq("product_id", pid_str) \
                    .eq("language_code", language_code.value) \
                    .maybe_single() \
                    .execute()
                if response and response.data:
                    return TranslationResponse(**response.data)
                return None
            except Exception as e:
                logger.error(f"Error fetching translation from Supabase: {e}. Checking in-memory store.")

        # In-memory fallback
        item = self._in_memory_store.get(pid_str, {}).get(language_code.value)
        if item:
            return TranslationResponse(**item)
        return None

    async def upsert_translation(
        self,
        product_id: UUID,
        language_code: SupportedLanguage,
        name: Optional[str] = None,
        description: Optional[str] = None,
    ) -> TranslationResponse:
        pid_str = str(product_id)
        now = datetime.utcnow()

        if self.supabase_client:
            try:
                payload = {
                    "product_id": pid_str,
                    "language_code": language_code.value,
                    "name": name,
                    "description": description,
                    "updated_at": now.isoformat(),
                }
                res = self.supabase_client.table("product_translations") \
                    .upsert(payload, on_conflict="product_id,language_code") \
                    .execute()
                if res.data:
                    return TranslationResponse(**res.data[0])
            except Exception as e:
                logger.error(f"Error upserting to Supabase: {e}. Falling back to in-memory store.")

        # In-memory store logic
        if pid_str not in self._in_memory_store:
            self._in_memory_store[pid_str] = {}

        existing = self._in_memory_store[pid_str].get(language_code.value)
        if existing:
            existing["name"] = name if name is not None else existing.get("name")
            existing["description"] = description if description is not None else existing.get("description")
            existing["updated_at"] = now
            record = existing
        else:
            record = {
                "id": uuid4(),
                "product_id": product_id,
                "language_code": language_code,
                "name": name,
                "description": description,
                "created_at": now,
                "updated_at": now,
            }
            self._in_memory_store[pid_str][language_code.value] = record

        return TranslationResponse(**record)


translation_repo = SupabaseTranslationRepository()
