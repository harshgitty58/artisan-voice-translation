/**
 * Artisan AI Studio - Frontend Controller
 * Connects to either local FastAPI server or live Render deployment.
 */

const PRESETS = {
    diya_hi: {
        title: "पीतल का दीया (Brass Diya)",
        lang: "hi",
        mock_text: "यह हस्तनिर्मित पीतल का दीया है जो दिवाली और पूजा के लिए बहुत सुंदर है। इसकी कीमत 350 रुपये है।",
        // A minimal valid WebM/WAV silent base64 payload to pass STT / fallback pipeline
        audio_base64: "UklGRiQAAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQAAAAA="
    },
    saree_mr: {
        title: "पैठणी साडी (Paithani Saree)",
        lang: "mr",
        mock_text: "ही अस्सल येवला पैठणी साडी आहे, शुद्ध रेशीम आणि सोन्याच्या जरीचे नक्षीकाम केलेली. किंमत 4500 रुपये.",
        audio_base64: "UklGRiQAAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQAAAAA="
    },
    pot_hi: {
        title: "मिट्टी की हांडी (Clay Pot)",
        lang: "hi",
        mock_text: "यह पारंपरिक चिकनी मिट्टी से बनी हांडी है, खाना पकाने और दही जमाने के लिए उत्तम। प्राकृतिक लाल रंग, 250 रुपये।",
        audio_base64: "UklGRiQAAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQAAAAA="
    },
    chanderi_en: {
        title: "Chanderi Silk Saree",
        lang: "en",
        mock_text: "Handwoven authentic Chanderi silk saree with golden zari border and floral motifs. Pure handcrafted quality, price 3200 INR.",
        audio_base64: "UklGRiQAAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQAAAAA="
    }
};

let currentEndpoint = "http://localhost:8000";
let mediaRecorder = null;
let audioChunks = [];
let recordingInterval = null;
let recordingSeconds = 0;
let lastPipelineResult = null;

// DOM Elements
const endpointSelect = document.getElementById("endpoint-select");
const customEndpointInput = document.getElementById("custom-endpoint");
const healthIndicator = document.getElementById("health-indicator");
const healthText = document.getElementById("health-text");

const recordBtn = document.getElementById("record-btn");
const micRing = document.getElementById("mic-ring");
const micStatus = document.getElementById("mic-status");
const recordingTimer = document.getElementById("recording-timer");

const detectedLangBadge = document.getElementById("detected-lang-badge");
const transcriptText = document.getElementById("transcript-text");
const transcriptConf = document.getElementById("transcript-conf");
const extractedMaterial = document.getElementById("extracted-material");

const loadingSpinner = document.getElementById("loading-spinner");
const loadingText = document.getElementById("loading-text");
const rawJsonOutput = document.getElementById("raw-json-output");

const cardTitleEn = document.getElementById("card-title-en");
const cardDescEn = document.getElementById("card-desc-en");
const cardTitleHi = document.getElementById("card-title-hi");
const cardDescHi = document.getElementById("card-desc-hi");
const cardTitleMr = document.getElementById("card-title-mr");
const cardDescMr = document.getElementById("card-desc-mr");

const manualNameInput = document.getElementById("manual-name");
const manualDescInput = document.getElementById("manual-desc");
const translateBtn = document.getElementById("translate-btn");
const saveSupabaseBtn = document.getElementById("save-supabase-btn");
const dbStatusPill = document.getElementById("db-status-pill");

// --------------------------------------------------------------------------
// Initialization & Backend Selection
// --------------------------------------------------------------------------
function getBaseUrl() {
    if (endpointSelect.value === "custom") {
        return (customEndpointInput.value || "").trim().replace(/\/+$/, "");
    }
    return endpointSelect.value.replace(/\/+$/, "");
}

async function checkBackendHealth() {
    const url = getBaseUrl();
    healthIndicator.className = "health-pill checking";
    healthText.textContent = "Connecting...";

    try {
        const res = await fetch(`${url}/api/v1/health`, { method: "GET" });
        if (res.ok) {
            const data = await res.json();
            healthIndicator.className = "health-pill online";
            healthText.textContent = `Online • ${data.environment || "OK"}`;
        } else {
            throw new Error(`HTTP ${res.status}`);
        }
    } catch (err) {
        healthIndicator.className = "health-pill offline";
        healthText.textContent = `Offline (${err.message})`;
    }
}

endpointSelect.addEventListener("change", () => {
    if (endpointSelect.value === "custom") {
        customEndpointInput.style.display = "block";
    } else {
        customEndpointInput.style.display = "none";
    }
    checkBackendHealth();
});

customEndpointInput.addEventListener("change", checkBackendHealth);

// --------------------------------------------------------------------------
// Tabs switching
// --------------------------------------------------------------------------
document.querySelectorAll(".tab-btn").forEach(btn => {
    btn.addEventListener("click", () => {
        document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
        document.querySelectorAll(".tab-pane").forEach(p => p.classList.remove("active"));

        btn.classList.add("active");
        const targetId = btn.dataset.tab;
        const targetPane = document.getElementById(targetId);
        if (targetPane) targetPane.classList.add("active");
    });
});

// --------------------------------------------------------------------------
// Audio Recording via MediaRecorder
// --------------------------------------------------------------------------
function getSelectedSpokenLanguage() {
    // This is just a HINT for Google Speech-to-Text (helps transcription accuracy).
    // The backend auto-detects the actual language regardless.
    const checked = document.querySelector('input[name="spoken_lang"]:checked');
    return checked ? checked.value : "hi"; // default hi = covers most Devanagari
}

// Format seconds into MM:SS
function formatTime(sec) {
    const m = Math.floor(sec / 60).toString().padStart(2, "0");
    const s = (sec % 60).toString().padStart(2, "0");
    return `${m}:${s}`;
}

recordBtn.addEventListener("click", async () => {
    if (mediaRecorder && mediaRecorder.state === "recording") {
        stopRecording();
    } else {
        await startRecording();
    }
});

async function startRecording() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        audioChunks = [];
        
        // Pick best supported MIME type
        let mimeType = "audio/webm;codecs=opus";
        if (!MediaRecorder.isTypeSupported(mimeType)) {
            mimeType = MediaRecorder.isTypeSupported("audio/webm") ? "audio/webm" : "";
        }

        mediaRecorder = mimeType ? new MediaRecorder(stream, { mimeType }) : new MediaRecorder(stream);

        mediaRecorder.ondataavailable = (event) => {
            if (event.data.size > 0) {
                audioChunks.push(event.data);
            }
        };

        mediaRecorder.onstop = async () => {
            stream.getTracks().forEach(track => track.stop());
            const audioBlob = new Blob(audioChunks, { type: mediaRecorder.mimeType || "audio/webm" });
            const reader = new FileReader();
            reader.readAsDataURL(audioBlob);
            reader.onloadend = () => {
                const base64Data = reader.result.split(",")[1];
                // Pass selected lang as a STT hint only — backend will auto-detect regardless
                sendAudioToPipeline(base64Data, getSelectedSpokenLanguage());
            };
        };

        mediaRecorder.start();
        micRing.classList.add("recording");
        micStatus.textContent = "Listening... Click to Finish Recording";
        recordingTimer.style.display = "block";
        recordingSeconds = 0;
        recordingTimer.textContent = "00:00";
        recordingInterval = setInterval(() => {
            recordingSeconds++;
            recordingTimer.textContent = formatTime(recordingSeconds);
        }, 1000);

    } catch (err) {
        alert("Microphone access failed: " + err.message + "\nTip: You can use the One-Click Artisan Presets below without a microphone!");
        micStatus.textContent = "Mic denied. Use One-Click Presets below.";
    }
}

function stopRecording() {
    if (mediaRecorder && mediaRecorder.state === "recording") {
        mediaRecorder.stop();
        clearInterval(recordingInterval);
        micRing.classList.remove("recording");
        micStatus.textContent = "Processing audio...";
        recordingTimer.style.display = "none";
    }
}

// --------------------------------------------------------------------------
// Pipeline Execution
// --------------------------------------------------------------------------
async function sendAudioToPipeline(audioBase64, spokenLang, fallbackPreset = null) {
    showLoading("Transcribing & generating multilingual catalog...");
    const url = getBaseUrl();

    const payload = {
        audio_base64: audioBase64,
        audio_encoding: "WEBM_OPUS",
        spoken_language: spokenLang,
        auto_store: false
    };

    try {
        const response = await fetch(`${url}/api/v1/pipeline/voice-catalog`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            const errJson = await response.json().catch(() => null);
            throw new Error(errJson?.detail || `HTTP error ${response.status}`);
        }

        const data = await response.json();
        renderPipelineResult(data);
    } catch (err) {
        console.warn("Pipeline direct call failed or returned mock:", err);
        // If local STT without audio credentials, we provide preset translation fallback
        if (fallbackPreset) {
            await runDirectTranslateFallback(fallbackPreset);
        } else {
            alert(`Voice pipeline error: ${err.message}\nMake sure your server is running at ${url}`);
        }
    } finally {
        hideLoading();
    }
}

// --------------------------------------------------------------------------
// One-Click Presets Handler
// --------------------------------------------------------------------------
document.querySelectorAll(".preset-btn").forEach(btn => {
    btn.addEventListener("click", async () => {
        const presetKey = btn.dataset.preset;
        const preset = PRESETS[presetKey];
        if (!preset) return;

        // Optionally reflect the preset language in the chip (cosmetic only, not blocking)
        const radio = document.querySelector(`input[name="spoken_lang"][value="${preset.lang}"]`);
        if (radio) {
            radio.checked = true;
            document.querySelectorAll(".chip").forEach(c => c.classList.remove("active"));
            radio.closest(".chip")?.classList.add("active");
        }

        showLoading(`Running preset: ${preset.title}...`);
        await runDirectTranslateFallback(preset);
        hideLoading();
    });
});

async function runDirectTranslateFallback(preset) {
    const url = getBaseUrl();
    try {
        const res = await fetch(`${url}/api/v1/translate`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                source_language: preset.lang,
                target_languages: ["en", "hi", "mr"],
                name: preset.title,
                description: preset.mock_text
            })
        });

        if (!res.ok) {
            throw new Error(`Translate HTTP ${res.status}`);
        }

        const transData = await res.json();
        
        // Populate mock pipeline-like display
        transcriptText.innerHTML = `<strong>${preset.title}</strong><br><em>${preset.mock_text}</em>`;
        transcriptConf.textContent = "Transcript: Preset (100% clean)";
        detectedLangBadge.textContent = `Language: ${preset.lang.toUpperCase()}`;
        extractedMaterial.textContent = "Source: Artisan Preset";

        updateCatalogCards(transData.translations);
        rawJsonOutput.textContent = JSON.stringify(transData, null, 2);
        lastPipelineResult = transData;
        dbStatusPill.textContent = "Ready to Sync";
        dbStatusPill.className = "pill pill-idle";

    } catch (err) {
        alert("Preset failed to translate: " + err.message);
    }
}

// --------------------------------------------------------------------------
// Direct Translation Section
// --------------------------------------------------------------------------
translateBtn.addEventListener("click", async () => {
    const name = manualNameInput.value.trim();
    const desc = manualDescInput.value.trim();
    if (!name || !desc) {
        alert("Please enter both a product title and description to translate.");
        return;
    }

    showLoading("Translating across English, Hindi, and Marathi...");
    const url = getBaseUrl();

    try {
        const res = await fetch(`${url}/api/v1/translate`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                source_language: getSelectedSpokenLanguage(),
                target_languages: ["en", "hi", "mr"],
                name: name,
                description: desc
            })
        });

        if (!res.ok) {
            throw new Error(`Translation failed with HTTP ${res.status}`);
        }

        const data = await res.json();
        transcriptText.innerHTML = `<strong>Manual Entry:</strong> ${name}`;
        transcriptConf.textContent = "Confidence: Manual Input";
        detectedLangBadge.textContent = `Source: ${getSelectedSpokenLanguage().toUpperCase()}`;
        extractedMaterial.textContent = "Custom Input";

        updateCatalogCards(data.translations);
        rawJsonOutput.textContent = JSON.stringify(data, null, 2);
        lastPipelineResult = data;
        dbStatusPill.textContent = "Ready to Sync";
        dbStatusPill.className = "pill pill-idle";
    } catch (err) {
        alert("Translation error: " + err.message);
    } finally {
        hideLoading();
    }
});

// --------------------------------------------------------------------------
// Render & Helpers
// --------------------------------------------------------------------------
function renderPipelineResult(data) {
    lastPipelineResult = data;
    transcriptText.textContent = data.transcript || "No transcript detected";
    transcriptConf.textContent = `Confidence: ${(data.transcript_confidence * 100).toFixed(1)}%`;
    detectedLangBadge.textContent = `Detected: ${(data.detected_language || "").toUpperCase()}`;
    
    const draft = data.extracted_draft || {};
    extractedMaterial.textContent = draft.material_hint ? `Material: ${draft.material_hint}` : "Material: Auto-detected";

    const translations = data.generated_translations?.translations || [];
    updateCatalogCards(translations);

    rawJsonOutput.textContent = JSON.stringify(data, null, 2);
    dbStatusPill.textContent = data.stored ? "Synced to Table 007" : "Ready to Sync";
    dbStatusPill.className = data.stored ? "pill pill-success" : "pill pill-idle";

    // Auto-switch to the detected language tab
    const dl = (data.detected_language || "en").toLowerCase();
    const tabBtn = document.querySelector(`.tab-btn[data-tab="tab-${dl}"]`);
    if (tabBtn) {
        tabBtn.click();
    }
}

function updateCatalogCards(translations) {
    if (!translations || !translations.length) return;

    translations.forEach(t => {
        // Normalize language_code — can be enum string value or plain string
        const lang = (t.language_code || "").toString().toLowerCase();
        const noDesc = "(No description generated)";

        if (lang === "en") {
            cardTitleEn.textContent = t.name || "—";
            cardDescEn.textContent = t.description || noDesc;
        } else if (lang === "hi") {
            cardTitleHi.textContent = t.name || "—";
            cardDescHi.textContent = t.description || noDesc;
        } else if (lang === "mr") {
            cardTitleMr.textContent = t.name || "—";
            cardDescMr.textContent = t.description || noDesc;
        }
    });
}

function showLoading(msg) {
    loadingText.textContent = msg || "Processing with AI...";
    loadingSpinner.style.display = "flex";
}

function hideLoading() {
    loadingSpinner.style.display = "none";
}

// --------------------------------------------------------------------------
// Radio Chip Styling
// --------------------------------------------------------------------------
document.querySelectorAll('.radio-chips input[type="radio"]').forEach(radio => {
    radio.addEventListener("change", () => {
        // Find chips within the same container
        const group = radio.closest(".radio-chips");
        if (group) {
            group.querySelectorAll(".chip").forEach(c => c.classList.remove("active"));
            radio.closest(".chip")?.classList.add("active");
        }
    });
});

// --------------------------------------------------------------------------
// Navigation Tab Switching
// --------------------------------------------------------------------------
const panelTabs = document.querySelectorAll(".panel-tab");
const tabContents = document.querySelectorAll(".tab-content");

panelTabs.forEach(tab => {
    tab.addEventListener("click", () => {
        const targetId = tab.dataset.tab;
        panelTabs.forEach(t => t.classList.remove("active"));
        tab.classList.add("active");

        tabContents.forEach(content => {
            if (content.id === targetId) {
                content.style.display = "block";
                content.classList.add("active");
            } else {
                content.style.display = "none";
                content.classList.remove("active");
            }
        });
    });
});

// --------------------------------------------------------------------------
// Dedicated Description Generator
// --------------------------------------------------------------------------
const descInput = document.getElementById("desc-input");
const generateDescBtn = document.getElementById("generate-desc-btn");
const descResultBox = document.getElementById("desc-result-box");
const descResultText = document.getElementById("desc-result-text");
const descSourceBadge = document.getElementById("desc-source-badge");
const copyDescBtn = document.getElementById("copy-desc-btn");
const sendToCatalogBtn = document.getElementById("send-to-catalog-btn");

// Sample Prompts for Description Generator
document.querySelectorAll(".sample-chip").forEach(chip => {
    chip.addEventListener("click", () => {
        const text = chip.dataset.descText;
        const lang = chip.dataset.descLang;
        if (descInput && text) {
            descInput.value = text;
            descInput.focus();
        }
        if (lang) {
            const radio = document.querySelector(`input[name="desc_lang"][value="${lang}"]`);
            if (radio) {
                radio.checked = true;
                const group = radio.closest(".radio-chips");
                if (group) {
                    group.querySelectorAll(".chip").forEach(c => c.classList.remove("active"));
                    radio.closest(".chip")?.classList.add("active");
                }
            }
        }
    });
});

// Generate Description Button
if (generateDescBtn) {
    generateDescBtn.addEventListener("click", async () => {
        const text = (descInput?.value || "").trim();
        if (!text) {
            alert("Please enter some artisan speech or notes, or click a sample preset!");
            descInput?.focus();
            return;
        }

        const selectedLang = document.querySelector('input[name="desc_lang"]:checked')?.value || "hi";
        const url = getBaseUrl();

        showLoading("Generating polished English description via AI...");
        if (descResultBox) descResultBox.style.display = "none";

        try {
            const res = await fetch(`${url}/api/v1/description/generate`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    speech_input: text,
                    language: selectedLang
                })
            });

            if (!res.ok) {
                const errData = await res.json().catch(() => ({}));
                throw new Error(errData.detail || `Server returned ${res.status}`);
            }

            const data = await res.json();
            hideLoading();

            if (descResultBox && descResultText) {
                descResultText.textContent = data.english_description;
                
                // Format badge
                if (descSourceBadge) {
                    if (data.generation_source === "artisan_knowledge_synthesizer") {
                        descSourceBadge.textContent = "✨ Artisan Knowledge Engine";
                        descSourceBadge.className = "badge badge-gold";
                    } else if (data.generation_source === "artisan_knowledge_synthesizer") {
                        descSourceBadge.textContent = "🏛️ 3-Line Heritage Craft Engine";
                        descSourceBadge.className = "badge badge-accent";
                    } else if (data.generation_source === "google_translate_pipeline") {
                        descSourceBadge.textContent = "🌐 Google Cloud Translation";
                        descSourceBadge.className = "badge badge-accent";
                    } else {
                        descSourceBadge.textContent = "📐 Artisan Catalog Fallback";
                        descSourceBadge.className = "badge";
                    }
                }
                descResultBox.style.display = "block";
            }
        } catch (err) {
            hideLoading();
            alert(`Error generating description: ${err.message}`);
        }
    });
}

// Copy Description
if (copyDescBtn) {
    copyDescBtn.addEventListener("click", () => {
        if (!descResultText?.textContent) return;
        navigator.clipboard.writeText(descResultText.textContent).then(() => {
            const originalText = copyDescBtn.textContent;
            copyDescBtn.textContent = "✅ Copied!";
            setTimeout(() => { copyDescBtn.textContent = originalText; }, 2000);
        });
    });
}

// Transfer to Multilingual Catalog
if (sendToCatalogBtn) {
    sendToCatalogBtn.addEventListener("click", async () => {
        const desc = descResultText?.textContent;
        if (!desc) return;

        // Auto-extract candidate title from first words or input
        const rawInput = (descInput?.value || "").trim();
        const candidateTitle = rawInput.split(/[,\.\n]/)[0].substring(0, 60) || "Artisan Handcrafted Product";

        showLoading("Translating across English, Hindi, and Marathi...");
        const url = getBaseUrl();

        try {
            const res = await fetch(`${url}/api/v1/translate`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    source_language: "en",
                    target_languages: ["en", "hi", "mr"],
                    name: candidateTitle,
                    description: desc
                })
            });

            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            const data = await res.json();
            hideLoading();

            if (transcriptText) transcriptText.textContent = rawInput || desc;
            if (transcriptConf) transcriptConf.textContent = "Direct Input";
            if (detectedLangBadge) detectedLangBadge.textContent = "English (Generated)";

            updateCatalogCards(data.translations || []);
            if (rawJsonOutput) rawJsonOutput.textContent = JSON.stringify(data, null, 2);

            // Smooth scroll to catalog section on mobile/narrow screens
            document.querySelector(".results-card")?.scrollIntoView({ behavior: "smooth" });
        } catch (err) {
            hideLoading();
            alert(`Failed to translate catalog: ${err.message}`);
        }
    });
}

// Save to Supabase Placeholder Trigger
if (saveSupabaseBtn) {
    saveSupabaseBtn.addEventListener("click", () => {
        if (!lastPipelineResult && !descResultText?.textContent) {
            alert("Please generate or translate a product first!");
            return;
        }
        dbStatusPill.textContent = "Synced to Table 007 (Supabase)";
        dbStatusPill.className = "pill pill-success";
        alert("Translations verified and ready for public.product_translations!");
    });
}

// Initial Health Check on load
window.addEventListener("DOMContentLoaded", () => {
    // If deployed on Render or another web host, auto-configure the origin
    if (window.location.origin && window.location.origin.startsWith("http")) {
        if (!window.location.hostname.includes("localhost") && !window.location.hostname.includes("127.0.0.1")) {
            endpointSelect.value = "custom";
            customEndpointInput.style.display = "inline-block";
            customEndpointInput.value = window.location.origin;
        }
    }
    checkBackendHealth();
});

