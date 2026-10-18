"""Command Line Interface for radox-suite."""

import argparse
import json
import os
import sys
from typing import Optional
from .client import RadoxClient
from .tempmail_lol import TempMailLolClient
from .registrar import RadoxRegistrar

CONFIG_PATH = os.path.expanduser("~/.radox_config.json")


def load_config() -> dict:
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def save_config(data: dict) -> None:
    current = load_config()
    current.update(data)
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(current, f, indent=2)


def get_api_key(args: argparse.Namespace) -> str:
    key = args.key or os.getenv("RADOX_API_KEY") or load_config().get("api_key")
    if not key:
        print("[!] No Radox API key found. Pass --key <KEY>, set RADOX_API_KEY, or run: radox save-key <KEY>")
        sys.exit(1)
    return key


def cmd_save_key(args: argparse.Namespace) -> None:
    if not args.key_value:
        print("[!] Please supply an API key.")
        sys.exit(1)
    save_config({"api_key": args.key_value.strip()})
    print(f"[✓] API key saved to {CONFIG_PATH}")


def cmd_models(args: argparse.Namespace) -> None:
    print("\n" + "=" * 70)
    print("           🌟 RADOX.AI MODEL CATALOG (33 Models Supported)")
    print("=" * 70)
    # If key is provided or saved, try live /v1/models
    key = args.key or os.getenv("RADOX_API_KEY") or load_config().get("api_key")
    if key:
        try:
            client = RadoxClient(api_key=key)
            models = client.list_models()
            for m in models:
                mid = m.get("id")
                print(f" • {mid}")
            print("=" * 70 + "\n")
            return
        except Exception as e:
            print(f"[i] Querying live /v1/models failed ({e}), displaying catalog from official schema:\n")

    # Static catalog parsed from radoxai.com/models
    catalog = [
        ("gemma-2-2b", "Google Gemma 2 2B", "$0.11 / 1M"),
        ("deepseek-v4-flash-0731", "DeepSeek-V4 Flash (304B)", "$0.11 / 1M"),
        ("gpt-5.6-luna", "OpenAI GPT-5.6 Luna", "$0.35 / 1M"),
        ("deepseek-v4-pro-0813", "DeepSeek-V4 Pro (1.6T)", "$0.55 / 1M"),
        ("qwen3.8-27b", "Alibaba Qwen 3.8 27B", "$0.57 / 1M"),
        ("seed-2.1-turbo", "ByteDance Seed 2.1 Turbo", "$0.92 / 1M"),
        ("seed-2.1-pro", "ByteDance Seed 2.1 Pro", "$1.15 / 1M"),
        ("kimi-k2.6", "Moonshot Kimi K2.6 (1.0T)", "$1.21 / 1M"),
        ("gemini-3.7-flash", "Google Gemini 3.7 Flash", "$1.24 / 1M"),
        ("glm-5.3", "Zhipu GLM-5.3 (753B)", "$1.35 / 1M"),
        ("glm-5.2", "Zhipu GLM-5.2 (753B)", "$1.35 / 1M"),
        ("qwen3.7-max", "Alibaba Qwen 3.7 Max", "$1.75 / 1M"),
        ("qwen3.8-max", "Alibaba Qwen 3.8 Max (2.4T)", "$1.75 / 1M"),
        ("muse-spark-1.1", "Meta Muse Spark 1.1", "$1.81 / 1M"),
        ("deepseek-v4-pro-max", "DeepSeek-V4 Pro Max", "$2.04 / 1M"),
        ("gemini-3.6-flash", "Google Gemini 3.6 Flash", "$2.49 / 1M"),
        ("grok-4.5", "xAI Grok 4.5", "$2.80 / 1M"),
        ("grok-4.6", "xAI Grok 4.6", "$2.80 / 1M"),
        ("claude-sonnet-5", "Anthropic Claude Sonnet 5", "$3.32 / 1M"),
        ("gpt-5.6-terra", "OpenAI GPT-5.6 Terra", "$3.57 / 1M"),
        ("gemini-3.1-pro", "Google Gemini 3.1 Pro", "$4.47 / 1M"),
        ("kimi-k3", "Moonshot Kimi K3 (2.8T)", "$4.97 / 1M"),
        ("claude-opus-5.5", "Anthropic Claude Opus 5.5", "$8.30 / 1M"),
        ("claude-opus-4.7", "Anthropic Claude Opus 4.7", "$8.30 / 1M"),
        ("claude-opus-4.6", "Anthropic Claude Opus 4.6", "$8.30 / 1M"),
        ("claude-opus-4.8", "Anthropic Claude Opus 4.8", "$8.30 / 1M"),
        ("claude-mythos-preview", "Anthropic Claude Mythos Preview", "$8.30 / 1M"),
        ("claude-opus-5", "Anthropic Claude Opus 5", "$8.30 / 1M"),
        ("gpt-5.5-pro", "OpenAI GPT-5.5 Pro", "$8.94 / 1M"),
        ("gpt-5.5", "OpenAI GPT-5.5", "$8.94 / 1M"),
        ("gpt-5.6-sol", "OpenAI GPT-5.6 Sol", "$8.94 / 1M"),
        ("claude-fable-5", "Anthropic Claude Fable 5", "$16.60 / 1M"),
        ("claude-fable-5.1", "Anthropic Claude Fable 5.1", "$16.60 / 1M"),
    ]

    print(f"{'MODEL ID':<26} {'NAME':<32} {'PRICE':<12}")
    print("-" * 70)
    for mid, name, price in catalog:
        print(f" • {mid:<24} {name:<32} {price:<12}")
    print("=" * 70 + "\n")


def cmd_chat(args: argparse.Namespace) -> None:
    key = get_api_key(args)
    client = RadoxClient(api_key=key)
    model = args.model or "deepseek-v4-flash-0731"
    prompt = args.prompt or "Hello! Introduce yourself in one sentence."

    print(f"[*] Sending prompt to {model} via Radox AI...")
    try:
        if args.no_stream:
            resp = client.chat_completion(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                stream=False
            )
            content = resp.get("choices", [{}])[0].get("message", {}).get("content", "")
            print(f"\n[Response]:\n{content}\n")
        else:
            print("\n[Response]:")
            for chunk in client.chat_completion(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                stream=True
            ):
                sys.stdout.write(chunk)
                sys.stdout.flush()
            print("\n")
    except Exception as e:
        print(f"[x] Error during chat completion: {e}")
        sys.exit(1)


def cmd_tempmail(args: argparse.Namespace) -> None:
    tmp = TempMailLolClient()
    if args.token:
        print(f"[*] Checking messages for token {args.token}...")
        try:
            emails = tmp.get_emails(args.token)
            if not emails:
                print("[i] Inbox is empty.")
                return
            for idx, em in enumerate(emails):
                print(f"\n--- Email #{idx + 1} ---")
                print(f"From   : {em.get('from')}")
                print(f"Subject: {em.get('subject')}")
                print(f"Body   :\n{em.get('body')}")
        except Exception as e:
            print(f"[x] Error checking inbox: {e}")
            sys.exit(1)
    else:
        print("[*] Generating new inbox on tempmail.lol...")
        try:
            res = tmp.create_inbox()
            addr = res["address"]
            token = res["token"]
            print("\n" + "=" * 55)
            print("         📧 TEMPORARY INBOX GENERATED")
            print("=" * 55)
            print(f" • Address : {addr}")
            print(f" • Token   : {token}")
            print("=" * 55)
            print(f"Check emails later with: radox tempmail --token {token}\n")
        except Exception as e:
            print(f"[x] Error generating inbox: {e}")
            sys.exit(1)


def cmd_register(args: argparse.Namespace) -> None:
    print("\n" + "=" * 65)
    print("        🚀 RADOX.AI AUTOMATED ACCOUNT REGISTRATION")
    print("=" * 65)

    email = args.email
    password = args.password or "RadoxPass!2026"
    name = args.name or "AI Developer"

    # If no email is provided, use tempmail.lol
    tmp_token = None
    if not email:
        print("[*] No email specified. Fetching disposable inbox from tempmail.lol...")
        try:
            tmp = TempMailLolClient()
            inbox = tmp.create_inbox()
            email = inbox["address"]
            tmp_token = inbox["token"]
            print(f"[+] Inbox created: {email}")
        except Exception as e:
            print(f"[!] tempmail.lol error: {e}. You can supply your own email with -e <email>.")
            sys.exit(1)

    reg = RadoxRegistrar()
    print(f"[*] Submitting registration to https://radoxai.com/register for {email}...")
    try:
        reg.register(name=name, email=email, password=password)
        print("[✓] User record registered successfully in Radox AI database!")
    except Exception as e:
        print(f"[!] Registration submission note: {e}")

    # Now verify login
    print("[*] Verifying login session...")
    try:
        login_res = reg.login(email=email, password=password)
        print(f"[+] Login state: {login_res}")
        if login_res.get("needs_email_verification"):
            print("\n" + "-" * 65)
            print("⚠️  ACCOUNT CREATED BUT REQUIRES 6-DIGIT EMAIL VERIFICATION CODE")
            print("-" * 65)
            print(f"Credentials:")
            print(f" • Email    : {email}")
            print(f" • Password : {password}")
            if tmp_token:
                print(f" • TempMail Token: {tmp_token}")
                print(f"\n[*] Waiting up to 60s for verification code to arrive at tempmail.lol...")
                code = tmp.wait_for_code(tmp_token, timeout_seconds=60)
                if code:
                    print(f"[✓] Received OTP Code: {code}")
                    if reg.verify_code(code):
                        print("[🎉] Email verified! Logged into dashboard!")
                    else:
                        print(f"[!] Could not auto-verify code {code}.")
                else:
                    print("[!] No OTP code arrived within 60s (Note: Radox AI's internal mail server may be failing).")
            print("-" * 65 + "\n")
        else:
            print("[🎉] Logged in directly to dashboard without verification gate!")
    except Exception as e:
        print(f"[x] Error during login check: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Radox AI Suite — Manage models, run completions, and automate registration."
    )
    parser.add_argument("--key", "-k", help="Radox API key (starts with cc_)")

    subparsers = parser.add_subparsers(dest="subcommand", help="Available subcommands")

    # save-key
    p_sk = subparsers.add_parser("save-key", help="Save API key to ~/.radox_config.json")
    p_sk.add_argument("key_value", help="API key value (starts with cc_)")

    # models
    subparsers.add_parser("models", help="List all 33 available AI models")

    # chat
    p_chat = subparsers.add_parser("chat", help="Send chat completion request")
    p_chat.add_argument("--model", "-m", default="deepseek-v4-flash-0731", help="Model ID")
    p_chat.add_argument("--prompt", "-p", default="Say hello in 5 words", help="User prompt")
    p_chat.add_argument("--no-stream", action="store_true", help="Disable streaming output")

    # tempmail
    p_tmp = subparsers.add_parser("tempmail", help="Generate or check tempmail.lol inbox")
    p_tmp.add_argument("--token", "-t", help="Check messages for this inbox token")

    # register
    p_reg = subparsers.add_parser("register", help="Register a new Radox AI account")
    p_reg.add_argument("--email", "-e", help="Custom email address (optional, default: tempmail.lol)")
    p_reg.add_argument("--password", "-p", help="Custom password (optional, default: RadoxPass!2026)")
    p_reg.add_argument("--name", "-n", default="AI Developer", help="User full name")

    args = parser.parse_args()

    if not args.subcommand:
        parser.print_help()
        sys.exit(0)

    dispatch = {
        "save-key": cmd_save_key,
        "models": cmd_models,
        "chat": cmd_chat,
        "tempmail": cmd_tempmail,
        "register": cmd_register,
    }

    dispatch[args.subcommand](args)


if __name__ == "__main__":
    main()
