"""Automated Registrar & Session Handler for radoxai.com."""

import re
import time
import requests
from typing import Dict, Any, Optional
from .tempmail_lol import TempMailLolClient


class RadoxRegistrar:
    BASE_URL = "https://radoxai.com"

    def __init__(self, user_agent: Optional[str] = None):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": user_agent or "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Origin": self.BASE_URL,
            "Referer": f"{self.BASE_URL}/register"
        })

    def get_csrf_token(self, url: str) -> str:
        resp = self.session.get(url, timeout=20)
        resp.raise_for_status()
        match = re.search(r'name="_token"\s+value="([^"]+)"', resp.text)
        if not match:
            match = re.search(r'name="csrf-token"\s+content="([^"]+)"', resp.text)
        if not match:
            raise RuntimeError(f"Could not extract CSRF token from {url}")
        return match.group(1)

    def register(
        self,
        name: str,
        email: str,
        password: str,
        phone: str = ""
    ) -> Dict[str, Any]:
        """
        Submits registration form.
        Radox AI creates user in DB even if its mailer throws HTTP 500.
        """
        csrf = self.get_csrf_token(f"{self.BASE_URL}/register")

        data = {
            "_token": csrf,
            "name": name,
            "email": email,
            "phone": phone,
            "password": password,
            "password_confirmation": password
        }

        resp = self.session.post(
            f"{self.BASE_URL}/register",
            data=data,
            allow_redirects=False,
            timeout=25
        )

        # Radox AI returns 500 when mailer fails to send welcome email,
        # but the user record IS created in database!
        if resp.status_code == 302:
            loc = resp.headers.get("Location", "")
            if "register" in loc:
                # Validation error
                r_err = self.session.get(loc)
                errors = re.findall(r'<p class="[^"]*text-red-[^"]*">([^<]+)</p>', r_err.text)
                err_msg = errors[0] if errors else "Validation failed"
                raise RuntimeError(f"Registration rejected: {err_msg}")
        elif resp.status_code == 500:
            # Backend mailer exception, account is created
            pass

        return {
            "email": email,
            "password": password,
            "status": "created_pending_verification"
        }

    def login(self, email: str, password: str) -> Dict[str, Any]:
        """Logs into Radox AI and checks post-login destination."""
        csrf = self.get_csrf_token(f"{self.BASE_URL}/login")
        data = {
            "_token": csrf,
            "email": email,
            "password": password
        }

        resp = self.session.post(
            f"{self.BASE_URL}/login",
            data=data,
            allow_redirects=False,
            timeout=25
        )

        if resp.status_code != 302:
            raise RuntimeError("Login failed: invalid credentials or blocked request.")

        target = resp.headers.get("Location", "")
        # Follow redirect
        r_dest = self.session.get(target, timeout=25)

        needs_verification = "verify-email" in r_dest.url
        return {
            "logged_in": True,
            "current_url": r_dest.url,
            "needs_email_verification": needs_verification
        }

    def verify_code(self, code: str) -> bool:
        """Submit 6-digit OTP code to /verify-email."""
        csrf = self.get_csrf_token(f"{self.BASE_URL}/verify-email")
        data = {
            "_token": csrf,
            "code": code.strip()
        }
        resp = self.session.post(
            f"{self.BASE_URL}/verify-email",
            data=data,
            allow_redirects=False,
            timeout=25
        )
        if resp.status_code == 302 and "dashboard" in resp.headers.get("Location", ""):
            return True
        return False
