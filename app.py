# =============================================================================
# app.py — Hu-Mate Assist | Flask Global Error Handler + Telegram Notifier
# Bot: CMUHumateBot
# =============================================================================
# SETUP:
#   1. Copy .env.example to .env and fill in your TELEGRAM_BOT_TOKEN.
#   2. pip install -r requirements.txt
#   3. python app.py
# =============================================================================

import os
import traceback
import re
from datetime import datetime, timezone

import requests
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from werkzeug.exceptions import HTTPException

# ---------------------------------------------------------------------------
# Environment & Configuration
# ---------------------------------------------------------------------------
load_dotenv()  # Reads variables from a local .env file (ignored in production)

# REQUIRED: Set TELEGRAM_BOT_TOKEN in your environment or .env file.
# Never commit the actual token to source control.
TELEGRAM_BOT_TOKEN: str = os.environ.get("TELEGRAM_BOT_TOKEN", "")

# The Chat ID that will receive error notifications.
# Hardcoded per project spec; move to env var (TELEGRAM_CHAT_ID) for flexibility.
TELEGRAM_CHAT_ID: str = os.environ.get("TELEGRAM_CHAT_ID", "8704682336")

# NOTE: URL is intentionally NOT built here at module level.
# It is constructed dynamically inside send_telegram_notification() so that
# the token is always read at call-time (safe for token rotation / late binding).
TELEGRAM_BASE_URL: str = "https://api.telegram.org"

# ---------------------------------------------------------------------------
# Flask Application
# ---------------------------------------------------------------------------
app = Flask(__name__)


# ---------------------------------------------------------------------------
# Helper: MarkdownV2 escaping
# ---------------------------------------------------------------------------
_MDV2_SPECIAL = r"\_*[]()~`>#+-=|{}.!"


def escape_mdv2(text: str) -> str:
    """Escape all MarkdownV2 special characters in plain text."""
    return re.sub(r"([" + re.escape(_MDV2_SPECIAL) + r"])", r"\\\1", str(text))


# ---------------------------------------------------------------------------
# Helper: Build the Telegram notification message
# ---------------------------------------------------------------------------
def build_error_message(exc: Exception) -> str:
    """
    Format a detailed error report using Telegram MarkdownV2 syntax.

    Sections (in order):
      - Title
      - Timestamp (UTC)
      - Request URL
      - Error Type
      - Error Message
      - Full Traceback (code block)
    """
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    request_url = escape_mdv2(request.url)
    error_type = escape_mdv2(type(exc).__name__)
    error_msg = escape_mdv2(str(exc))

    # Full traceback — placed inside a MarkdownV2 code block.
    # Backticks inside a code block would break the fence; replace them.
    tb_raw = traceback.format_exc()
    tb_safe = tb_raw.replace("`", "'")

    message = (
        "🚨 *System Error: Hu\\-Mate Assist* 🚨\n"
        "\n"
        f"*Timestamp \\(UTC\\):* `{escape_mdv2(timestamp)}`\n"
        f"*Request URL:* `{request_url}`\n"
        f"*Error Type:* `{error_type}`\n"
        f"*Error Message:* `{error_msg}`\n"
        "\n"
        "*Traceback:*\n"
        f"```python\n{tb_safe}\n```"
    )
    return message


# ---------------------------------------------------------------------------
# Helper: Send message to Telegram
# ---------------------------------------------------------------------------
def send_telegram_notification(message: str) -> None:
    """
    POST the formatted error message to the CMUHumateBot Telegram endpoint.
    Failures are logged but never re-raised to avoid masking the original error.
    The API URL is built here (not at module level) so token rotation is safe.
    """
    token = os.environ.get("TELEGRAM_BOT_TOKEN", TELEGRAM_BOT_TOKEN)
    if not token:
        app.logger.warning(
            "TELEGRAM_BOT_TOKEN is not set — skipping Telegram notification."
        )
        return

    api_url = f"{TELEGRAM_BASE_URL}/bot{token}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "MarkdownV2",
    }

    try:
        resp = requests.post(api_url, json=payload, timeout=10)
        resp.raise_for_status()
        app.logger.info("Telegram notification sent successfully.")
    except requests.RequestException as req_err:
        app.logger.error(f"Failed to send Telegram notification: {req_err}")


# ---------------------------------------------------------------------------
# Global Error Handler
# ---------------------------------------------------------------------------
@app.errorhandler(Exception)
def handle_exception(exc: Exception):
    """
    Catch-all handler for every unhandled exception in the Flask application.

    - HTTPException subclasses (404, 405, etc.) are passed through as proper
      HTTP responses — Telegram alerts only fire for server errors (5xx).
    - All other exceptions trigger a Telegram notification and return a clean
      JSON 500 response so the client always gets a structured reply.
    """
    # Let Werkzeug handle expected HTTP errors (4xx) gracefully.
    if isinstance(exc, HTTPException):
        return jsonify(error=exc.name, description=exc.description), exc.code

    # Log the full traceback server-side.
    app.logger.exception("Unhandled exception caught by global error handler:")

    # Build and dispatch the Telegram alert.
    message = build_error_message(exc)
    send_telegram_notification(message)

    # Return a clean JSON 500 to the client.
    return (
        jsonify(
            {
                "error": "Internal Server Error",
                "message": "An unexpected error occurred. The team has been notified.",
            }
        ),
        500,
    )


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.route("/")
def index():
    """Health-check / welcome route."""
    return jsonify(
        {
            "project": "Hu-Mate Assist",
            "bot": "CMUHumateBot",
            "status": "ok",
            "message": "Flask application is running successfully.",
        }
    )


@app.route("/trigger-error")
def trigger_error():
    """
    Test route that intentionally raises a ZeroDivisionError.
    Visit this endpoint to verify the Telegram notification pipeline end-to-end.
    """
    app.logger.info("Triggering intentional ZeroDivisionError for testing...")
    result = 1 / 0  # deliberately raises ZeroDivisionError
    return jsonify(result=result)  # never reached


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # debug=True is fine for local testing; NEVER enable in production.
    # In production, serve with a WSGI server: gunicorn app:app
    app.run(debug=True, host="0.0.0.0", port=5000)
