# Hu-Mate Assist

A production-ready Flask application with a **global error handler** that sends
detailed, formatted error notifications to a Telegram chat via **CMUHumateBot**.

---

## Features

- Global `@app.errorhandler(Exception)` catches all unhandled server errors
- Instant Telegram alert with timestamp, request URL, error type, message, and full traceback
- MarkdownV2-formatted Telegram messages with syntax-highlighted tracebacks
- Secure token management via environment variables — token never hardcoded
- Clean JSON error responses for API consumers

---

## Project Structure

```
hu-mate-assist/
├── app.py              # Flask application & error handler
├── requirements.txt    # Python dependencies
├── .env.example        # Environment variable template
├── .gitignore          # Excludes .env and runtime files
└── README.md
```

---

## Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/<your-username>/hu-mate-assist.git
cd hu-mate-assist
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
cp .env.example .env
```

Open `.env` and set your bot token:

```
TELEGRAM_BOT_TOKEN=your_actual_token_here
```

> **Security note:** `.env` is listed in `.gitignore` and will never be
> committed. Keep your token secret.

### 5. Run the app

```bash
python app.py
```

The server starts at `http://localhost:5000`.

---

## Test Routes

| Route | Description |
|---|---|
| `GET /` | Health check — returns project info |
| `GET /trigger-error` | Intentionally raises `ZeroDivisionError` to test Telegram alert |

---

## Telegram Notification Format

```
🚨 System Error: Hu-Mate Assist 🚨

Timestamp (UTC): 2026-05-17 10:30:00
Request URL:     http://localhost:5000/trigger-error
Error Type:      ZeroDivisionError
Error Message:   division by zero

Traceback:
  ...full traceback here...
```

---

## Production Deployment

Use a WSGI server instead of the built-in Flask dev server:

```bash
pip install gunicorn
gunicorn app:app --bind 0.0.0.0:8000
```

Set `TELEGRAM_BOT_TOKEN` as a real environment variable on your server
(not from a `.env` file) for maximum security.

---

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `TELEGRAM_BOT_TOKEN` | ✅ Yes | Token from @BotFather for CMUHumateBot |
| `TELEGRAM_CHAT_ID` | Optional | Override the default chat ID (8704682336) |

---

## Dependencies

See `requirements.txt`:

```
Flask>=3.0.0
python-dotenv>=1.0.0
requests>=2.31.0
```
