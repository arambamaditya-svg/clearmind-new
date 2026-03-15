# backend/model_config.py - UPDATED FEBRUARY 2026
import os
OPENROUTER_API_KEY = os.environ.get('OPENROUTER_API_KEY')



OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# ===== YOUR WORKING MODELS =====
MODELS = {
    # M1: Extractor - Trinity Large (good at pulling facts)
    "extractor": {
        "model": "arcee-ai/trinity-large-preview:free",
        "description": "Extracts question, answer, thinking from student input"
    },
    
    # M2: Reasoner - Trinity Mini (faster, still good)
    "reasoner": {
        "model": "arcee-ai/trinity-mini:free",
        "description": "Identifies error type and root cause"
    },
    
    # M3: Explainer - Nemotron Nano (natural, warm)
    "explainer": {
        "model": "nvidia/nemotron-nano-9b-v2:free",
        "description": "Warm, direct explanations using 'you'"
    }
}

OPENROUTER_HEADERS = {
    "HTTP-Referer": "http://localhost:5000",
    "X-Title": "ClearMind"
}