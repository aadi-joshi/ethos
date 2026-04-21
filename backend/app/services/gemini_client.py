from __future__ import annotations

import google.generativeai as genai

from app.config.settings import get_settings


class GeminiClient:
    def __init__(self) -> None:
        self.settings = get_settings()
        self._model = None

        if self.settings.gemini_api_key:
            genai.configure(api_key=self.settings.gemini_api_key)
            self._model = genai.GenerativeModel(self.settings.gemini_model)

    @property
    def is_configured(self) -> bool:
        return self._model is not None

    def generate_text(self, prompt: str) -> str:
        if not self._model:
            raise RuntimeError("Gemini client is not configured.")

        response = self._model.generate_content(prompt)
        return (response.text or "").strip()
