
import os
import asyncio
import logging
import threading

from flask import Flask, jsonify
from pyrogram import Client

# ---------------- CONFIG ----------------

API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "").strip()
SESSION_STRING = os.getenv("SESSIONS", "").strip()
PORT = int(os.getenv("PORT", "10000"))

# ---------------- LOGGING ----------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger("SEM-VC-JOINER")

# ---------------- FLASK ----------------

app = Flask(__name__)

telegram_status = {
    "connected": False,
    "user": None,
    "error": None
}


@app.route("/")
def home():
    return jsonify({
        "project": "SEM VC JOINER",
        "status": "online",
        "telegram_connected": telegram_status["connected"]
    })


@app.route("/health")
def health():
    return jsonify({
        "status": "healthy",
        "telegram_connected": telegram_status["connected"]
    }), 200


@app.route("/status")
def status():
    return jsonify(telegram_status)


# ---------------- TELEGRAM ----------------

async def telegram_manager():

    if not API_ID or not API_HASH or not SESSION_STRING:
        logger.error(
            "Missing environment variables: "
            "API_ID, API_HASH or SESSIONS"
        )
        telegram_status["error"] = "Missing environment variables"
        return

    client = Client(
        name="sem_vc_joiner",
        api_id=API_ID,
        api_hash=API_HASH,
        session_string=SESSION_STRING,
        in_memory=True
    )

    started = False

    try:
        logger.info("Connecting to Telegram...")

        await client.start()
        started = True

        me = await client.get_me()

        telegram_status["connected"] = True
        telegram_status["user"] = (
            me.username or me.first_name or "Telegram User"
        )
        telegram_status["error"] = None

        logger.info(
            "Telegram connected successfully: %s",
            telegram_status["user"]
        )

        # Keep Telegram client running
        await asyncio.Event().wait()

    except Exception as e:
        telegram_status["connected"] = False
        telegram_status["error"] = str(e)

        logger.exception("Pyrogram connection failed")

    finally:
        if started:
            try:
                await client.stop()
                logger.info("Telegram client stopped.")
            except Exception:
                logger.exception("Error while stopping Telegram client")

        telegram_status["connected"] = False


# ---------------- THREAD ----------------

def start_telegram():
    try:
        asyncio.run(telegram_manager())
    except Exception:
        logger.exception("Telegram thread crashed")


# ---------------- MAIN ----------------

if __name__ == "__main__":

    logger.info("SEM VC JOINER starting...")

    telegram_thread = threading.Thread(
        target=start_telegram,
        name="TelegramThread",
        daemon=True
    )

    telegram_thread.start()

    app.run(
        host="0.0.0.0",
        port=PORT,
        debug=False,
        use_reloader=False
    )
