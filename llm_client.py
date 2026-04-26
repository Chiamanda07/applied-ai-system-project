"""
Gemini client wrapper used by StudyBot.

Handles:
- Configuring the Gemini client from the GEMINI_API_KEY environment variable
- RAG style answers that use only retrieved snippets
- Quiz generation from study material
"""

import os
import re
import json
import google.generativeai as genai

GEMINI_MODEL_NAME = "gemini-2.5-flash"


class GeminiClient:

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError(
                "Missing GEMINI_API_KEY environment variable. "
                "Set it in your shell or .env file to enable LLM features."
            )

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(GEMINI_MODEL_NAME)

    # -----------------------------------------------------------
    # RAG: answer a question using retrieved snippets
    # -----------------------------------------------------------

    def answer_from_snippets(self, query, snippets):
        """
        snippets: list of (filename, text) tuples selected by StudyBot.retrieve
        """
        if not snippets:
            return "I don't have enough information in the provided material to answer that."

        context_blocks = []
        for filename, text in snippets:
            context_blocks.append(f"[{filename}]\n{text}\n")

        context = "\n\n".join(context_blocks)

        prompt = f"""
You are a helpful study assistant helping a student understand their study material.

You will receive:
- A student question
- A small set of relevant excerpts from their study material

Your job:
- Answer the question using only the information in the excerpts.
- If the excerpts do not contain enough information, say so clearly.

Excerpts:
{context}

Student question:
{query}

Rules:
- Use only the information in the excerpts. Do not add outside knowledge.
- If the excerpts are not enough to answer confidently, reply exactly:
  "I don't have enough information in the provided material to answer that."
- Keep your answer clear and concise.
"""
        response = self.model.generate_content(prompt)
        return (response.text or "").strip()

    # -----------------------------------------------------------
    # Quiz generation over study material
    # -----------------------------------------------------------

    def generate_quiz(self, context, num_questions=5):
        """
        Prompts Gemini to generate multiple choice questions from the context.
        Returns a list of dicts: {question, options: {A,B,C,D}, answer}
        """
        prompt = f"""
You are a quiz generator. Create {num_questions} multiple choice questions based on the study material below.

Return ONLY a JSON array with no extra text, using this exact format:
[
  {{
    "question": "...",
    "options": {{"A": "...", "B": "...", "C": "...", "D": "..."}},
    "answer": "A"
  }}
]

Rules:
- Each question must have exactly 4 options labeled A, B, C, D.
- The "answer" field must be the letter of the correct option.
- Questions should test understanding of key concepts, not just definitions.

Study material:
{context}
"""
        response = self.model.generate_content(prompt)
        text = (response.text or "").strip()

        # Strip markdown code fences if Gemini wraps the JSON in them
        text = re.sub(r"^```[a-z]*\n?", "", text)
        text = re.sub(r"\n?```$", "", text).strip()

        return json.loads(text)
