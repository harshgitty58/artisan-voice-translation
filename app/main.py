import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api.v1.translations import router as translations_router
from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=(
        "Artisan AI Business Copilot — Speech Translation & Multilingual Catalog Service. "
        "Supports English (en), Hindi (hi), and Marathi (mr) content per Table 007 specification. "
        "Integrates with Google Cloud Speech-to-Text and Google Cloud Translation."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Enable CORS for web and mobile frontends
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API routers
app.include_router(translations_router, prefix=settings.API_V1_STR)

# Mount Web Studio UI if directory exists
UI_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "sample_ui")
if os.path.isdir(UI_DIR):
    app.mount("/ui", StaticFiles(directory=UI_DIR, html=True), name="ui")


@app.get("/", tags=["Root"])
async def root():
    return {
        "module": "Artisan AI Business Copilot — Speech Translation Service",
        "version": "1.0.0",
        "studio_ui": "/ui",
        "docs": "/docs",
        "health": f"{settings.API_V1_STR}/health",
        "endpoints": {
            "voice_pipeline":     f"{settings.API_V1_STR}/pipeline/voice-catalog",
            "speech_transcribe":  f"{settings.API_V1_STR}/speech/transcribe",
            "detect_language":    f"{settings.API_V1_STR}/speech/detect-language",
            "ai_translate":       f"{settings.API_V1_STR}/translate",
            "product_translations": f"{settings.API_V1_STR}/products/{{product_id}}/translations",
            "product_catalog":    f"{settings.API_V1_STR}/products/{{product_id}}/catalog?lang=hi",
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=True)
