# backend/ai_brain.py - Clean 3-model pipeline
"""
M1: Trinity Large - Extracts thinking
M2: Trinity Mini - Identifies error
M3: Nemotron Nano - Explains warmly
"""

import json
import re
from typing import Dict, Any, Optional
from openai import OpenAI
import httpx

from model_config import (
    OPENROUTER_API_KEY, OPENROUTER_BASE_URL, OPENROUTER_HEADERS,
    MODELS
)
from prompts import (
    EXTRACTOR_PROMPT, REASONER_PROMPT, EXPLAINER_PROMPT
)


class ClearMindAI:
    def __init__(self):
        self.client = OpenAI(
            api_key=OPENROUTER_API_KEY,
            base_url=OPENROUTER_BASE_URL,
            http_client=httpx.Client(proxies=None, follow_redirects=True),
            default_headers=OPENROUTER_HEADERS
        )
        self.models = MODELS
    
    def call_model(self, model_key: str, prompt: str, temperature: float = 0.4) -> Optional[str]:
        """Call a model and return response"""
        model_id = self.models[model_key]["model"]
        
        try:
            response = self.client.chat.completions.create(
                model=model_id,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=500,
                timeout=15
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"    ❌ Error: {str(e)[:100]}")
            return None
    
    def _get_extractor_prompt(self, text: str) -> str:
        return EXTRACTOR_PROMPT.format(student_input=text)

    def _get_reasoner_prompt(self, thinking: str) -> str:
        return REASONER_PROMPT.format(thinking_process=thinking)

    def _get_explainer_prompt(self, core_issue: str) -> str:
        return EXPLAINER_PROMPT.format(core_issue=core_issue)
    
    def _extract_json(self, text: str) -> Optional[Dict]:
        if not text:
            return None
        try:
            match = re.search(r'\{.*\}', text, re.DOTALL)
            if match:
                return json.loads(match.group())
        except:
            pass
        return None
    
    def process(self, text: str) -> Dict[str, Any]:
        """Run 3-model pipeline"""
        print("\n🧠 Starting...")
        
        # STEP 1: Extract thinking
        extract_prompt = self._get_extractor_prompt(text)
        extract_result = self.call_model("extractor", extract_prompt, 0.2)
        
        if extract_result:
            extracted = self._extract_json(extract_result)
            thinking = extracted.get("thinking_process", text) if extracted else text
        else:
            thinking = text
        
        # STEP 2: Identify error
        reason_prompt = self._get_reasoner_prompt(thinking)
        reason_result = self.call_model("reasoner", reason_prompt, 0.2)
        
        if reason_result:
            reasoned = self._extract_json(reason_result)
            core_issue = reasoned.get("core_issue", "unclear what went wrong") if reasoned else "unclear what went wrong"
        else:
            core_issue = "unclear what went wrong"
        
        # STEP 3: Explain to student
        explain_prompt = self._get_explainer_prompt(core_issue)
        explanation = self.call_model("explainer", explain_prompt, 0.5)
        
        if not explanation:
            explanation = "Let's work through this together. What were you thinking?"
        
        print("✅ Done\n")
        
        return {
            "response": explanation.strip()
        }


ai_brain = ClearMindAI()