# Radox AI Suite (`radox-suite`)

Toolkit otomasi CLI & Python Client untuk **Radox AI** (`https://radoxai.com`) dengan integrasi disposable email **TempMail.lol**.

---

## ⚡ Fitur Utama

- **OpenAI-Compatible Engine**: Interface inferensi langsung ke `https://radoxai.com/v1/chat/completions` dan `https://radoxai.com/v1/models`.
- **Model Catalog Explorer**: Mendukung 33 model mutakhir (Claude Opus 5.5, Claude Sonnet 5, GPT-5.6 Sol/Luna/Terra, Gemini 3.7 Flash, DeepSeek-V4, Kimi K3, GLM-5.3, dll).
- **TempMail.lol Integration**: Generator inbox disposable email otomatis via `https://api.tempmail.lol/v2`.
- **Automated Registrar**: Pendaftaran akun otomatis ke `https://radoxai.com/register` dengan penanganan CSRF, bypass proteksi form, dan deteksi validasi domain.

---

## 🚀 Setup & Instalasi

CLI `radox` sudah otomatis terpasang secara global di `/usr/local/bin/radox`:

```bash
# Simpan Radox API Key (format: cc_...)
radox save-key cc_...

# Atau set via Environment Variable
export RADOX_API_KEY="cc_..."
```

---

## 📖 Panduan Penggunaan CLI

### 1. Eksplorasi 33 Model AI
```bash
radox models
```

### 2. Kirim Chat Completion / Testing Inferensi
```bash
# Streaming completion (default)
radox chat --model "deepseek-v4-flash-0731" --prompt "Jelaskan apa itu Radox AI dalam 2 kalimat."

# Non-streaming
radox chat --model "claude-sonnet-5" --prompt "Hello" --no-stream
```

### 3. Generate Temporary Email via TempMail.lol
```bash
# Buat inbox baru
radox tempmail

# Cek pesan masuk berdasarkan token
radox tempmail --token <TOKEN_INBOX>
```

### 4. Pendaftaran Akun Otomatis
```bash
# Registrasi otomatis (menggunakan tempmail.lol)
radox register

# Registrasi dengan email custom
radox register --email "user@domain.com" --password "Password123!"
```

---

## 🐍 Penggunaan sebagai Python Library

```python
from radox_suite import RadoxClient, TempMailLolClient, RadoxRegistrar

# 1. Menggunakan Client Inferensi
client = RadoxClient(api_key="cc_your_api_key_here")
res = client.chat_completion(
    model="deepseek-v4-flash-0731",
    messages=[{"role": "user", "content": "Hello!"}]
)
print(res["choices"][0]["message"]["content"])

# 2. Menggunakan TempMail.lol Client
tmp = TempMailLolClient()
inbox = tmp.create_inbox()
print("Temporary email:", inbox["address"])
```
