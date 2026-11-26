
import os
import asyncio
import logging
import threading

from flask import Flask, jsonify
from pyrogram import Client
from pyrogram.errors import (
    AuthKeyUnregistered,
    SessionRevoked
)

# ---------------- CONFIG ----------------

API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
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

@app.route("/")
def home():
    return jsonify({
        "project": "SEM VC JOINER",
        "status": "online"
    })

@app.route("/health")
def health():
    return jsonify({"status": "healthy"}), 200

# ---------------- PYROGRAM ----------------

async def telegram_manager():

    if not API_ID or not API_HASH or not SESSION_STRING:
        logger.error("API_ID, API_HASH or SESSIONS is missing.")
        return

    client = Client(
        name="sem_vc_joiner",
        api_id=API_ID,
        api_hash=API_HASH,
        session_string=SESSION_STRING,
        in_memory=True
    )

    try:
        await client.start()

        me = await client.get_me()

        logger.info(
            "Pyrogram connected successfully: %s",
            me.first_name or "Telegram User"
        )

        # Keep client connected while service is running.
        await asyncio.Event().wait()

    except (AuthKeyUnregistered, SessionRevoked):
        logger.error("Session is revoked or no longer authorized.")

    except Exception as error:
        logger.error(
            "Pyrogram connection failed: %s",
            type(error).__name__
        )

    finally:
        try:
            await client.stop()
        except Exception:
            pass

def start_telegram():
    asyncio.run(telegram_manager())

# ---------------- START ----------------

if __name__ == "__main__":

    threading.Thread(
        target=start_telegram,
        daemon=True
    ).start()

    logger.info("SEM VC JOINER starting...")

    app.run(
        host="0.0.0.0",
        port=PORT,
        use_reloader=False
    )
