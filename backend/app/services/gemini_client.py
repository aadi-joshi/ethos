from __future__ import annotations

import time

from google import genai

from app.config.settings import get_settings

_RETRY_DELAYS = [5, 10, 20]  # seconds — respects 15 RPM free-tier limit


class GeminiClient:
    def __init__(self) -> None:
        self.settings = get_settings()
        self._client = None
        self._model_name = self.settings.gemini_model

        if self.settings.gemini_api_key:
            self._client = genai.Client(api_key=self.settings.gemini_api_key)

    @property
    def is_configured(self) -> bool:
        return self._client is not None

    def generate_text(self, prompt: str) -> str:
        if not self._client:
            raise RuntimeError("Gemini client is not configured.")

        last_err: Exception | None = None
        for delay in [0] + _RETRY_DELAYS:
            if delay:
                time.sleep(delay)
            try:
                response = self._client.models.generate_content(
                    model=self._model_name,
                    contents=prompt,
                )
                return (response.text or "").strip()
            except Exception as e:
                err_str = str(e)
                if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str or "quota" in err_str.lower():
                    last_err = e
                    continue
                raise

        raise RuntimeError(f"Gemini rate limit exceeded after retries: {last_err}")
