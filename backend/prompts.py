# backend/prompts.py - Ultra simple, human-focused

# ===== M1: EXTRACTOR - Just get the facts =====
EXTRACTOR_PROMPT = """Student wrote: "{student_input}"

Extract what they were thinking. Return ONLY this JSON:
{{"thinking_process": "their exact reasoning"}}"""

# ===== M2: REASONER - Identify the core issue =====
REASONER_PROMPT = """Student's thinking: "{thinking_process}"

What's the main error in their thinking? Return ONLY this JSON:
{{"core_issue": "one sentence explaining the mistake"}}"""

# ===== M3: EXPLAINER - Talk directly to student =====
EXPLAINER_PROMPT = """The student's mistake: {core_issue}

Write 2-3 warm, natural sentences directly to the student:
- Explain what went wrong (use "you")
- Help them understand how to fix it
- Be encouraging, like a friend helping

No robots. No lists. Just flowing conversation."""