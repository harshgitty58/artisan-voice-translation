import httpx, json, sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

payload = {
    "audio_base64": "UklGRiQAAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQAAAAA=",
    "audio_encoding": "WEBM_OPUS",
    "spoken_language": "mr",
    "auto_store": False
}

print("Calling pipeline (may take ~30s for Qwen on Colab)...")
r = httpx.post("http://localhost:8000/api/v1/pipeline/voice-catalog", json=payload, timeout=90)
data = r.json()

# Save full response to file for inspection
with open("pipeline_result.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("Status:", r.status_code)
print("Detected lang:", data.get("detected_language"))
print("Is mock:", data.get("is_mock"))
print("Transcript (first 80 chars):", str(data.get("transcript", ""))[:80])
print()

for t in data.get("generated_translations", {}).get("translations", []):
    lang = t["language_code"]
    name = str(t.get("name", ""))[:80]
    desc = str(t.get("description", ""))[:120]
    print(f"[{lang}] Title: {name}")
    print(f"[{lang}] Desc : {desc}")
    print()

print("Full result saved to pipeline_result.json")
