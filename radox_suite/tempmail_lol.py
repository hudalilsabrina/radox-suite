"""TempMail.lol API Client for radox-suite."""

import time
import requests
from typing import Dict, List, Optional, Any


class TempMailLolClient:
    """Client for https://api.tempmail.lol/v2 API."""
    BASE_URL = "https://api.tempmail.lol/v2"

    def __init__(self, api_key: Optional[str] = None, timeout: int = 15):
        self.api_key = api_key
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "RadoxSuite/1.0 (TempMailClient)",
            "Accept": "application/json"
        })
        if self.api_key:
            self.session.headers["Authorization"] = f"Bearer {self.api_key}"

    def create_inbox(self, domain: Optional[str] = None, prefix: Optional[str] = None) -> Dict[str, str]:
        """
        Creates a temporary inbox.
        Returns: {"address": "...", "token": "..."}
        """
        payload = {}
        if domain:
            payload["domain"] = domain
        if prefix:
            payload["prefix"] = prefix

        resp = self.session.post(f"{self.BASE_URL}/inbox/create", json=payload, timeout=self.timeout)
        if resp.status_code == 429:
            raise RuntimeError("TempMail.lol Rate Limit reached. Please wait ~60s before retrying.")
        resp.raise_for_status()
        data = resp.json()
        return {
            "address": data.get("address", ""),
            "token": data.get("token", "")
        }

    def get_emails(self, token: str) -> List[Dict[str, Any]]:
        """Fetch emails for a given inbox token."""
        resp = self.session.get(f"{self.BASE_URL}/inbox", params={"token": token}, timeout=self.timeout)
        if resp.status_code == 429:
            raise RuntimeError("TempMail.lol Rate Limit reached.")
        resp.raise_for_status()
        data = resp.json()
        if data.get("expired"):
            raise RuntimeError("TempMail token has expired.")
        return data.get("emails") or []

    def wait_for_code(self, token: str, timeout_seconds: int = 60, poll_interval: int = 3) -> Optional[str]:
        """Poll inbox until an email with a 6-digit verification code arrives."""
        import re
        start_time = time.time()
        while time.time() - start_time < timeout_seconds:
            try:
                emails = self.get_emails(token)
                for email in emails:
                    body = email.get("body", "") + " " + (email.get("html") or "") + " " + email.get("subject", "")
                    match = re.search(r"\b(\d{6})\b", body)
                    if match:
                        return match.group(1)
            except Exception:
                pass
            time.sleep(poll_interval)
        return None
