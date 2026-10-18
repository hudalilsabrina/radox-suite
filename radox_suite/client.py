"""Radox AI API Client: OpenAI-compatible interface for Radox AI."""

import json
from typing import Any, Dict, List, Optional, Generator
import requests


class RadoxClient:
    BASE_URL = "https://radoxai.com/v1"

    def __init__(self, api_key: str, timeout: int = 60):
        self.api_key = api_key.strip()
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "RadoxSuite/1.0"
        })

    def list_models(self) -> List[Dict[str, Any]]:
        """Fetch list of active models available on Radox AI."""
        resp = self.session.get(f"{self.BASE_URL}/models", timeout=self.timeout)
        if not resp.ok:
            raise RuntimeError(f"Radox API Error ({resp.status_code}): {resp.text}")
        data = resp.json()
        return data.get("data", [])

    def chat_completion(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False
    ) -> Any:
        """Send chat completion request to Radox AI."""
        payload: Dict[str, Any] = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "stream": stream
        }
        if max_tokens:
            payload["max_tokens"] = max_tokens

        resp = self.session.post(
            f"{self.BASE_URL}/chat/completions",
            json=payload,
            timeout=self.timeout,
            stream=stream
        )

        if not resp.ok:
            raise RuntimeError(f"Radox API Error ({resp.status_code}): {resp.text}")

        if stream:
            return self._stream_response(resp)

        return resp.json()

    def _stream_response(self, resp: requests.Response) -> Generator[str, None, None]:
        for line in resp.iter_lines():
            if not line:
                continue
            decoded = line.decode("utf-8")
            if decoded.startswith("data: "):
                data_str = decoded[6:].strip()
                if data_str == "[DONE]":
                    break
                try:
                    chunk = json.loads(data_str)
                    delta = chunk.get("choices", [{}])[0].get("delta", {})
                    content = delta.get("content", "")
                    if content:
                        yield content
                except Exception:
                    pass
