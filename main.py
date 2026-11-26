
import os
import asyncio
import logging
import threading

from flask import Flask, jsonify
from telethon import TelegramClient
from telethon.sessions import StringSession

# ---------------- CONFIG ----------------

API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")

SESSIONS = [
    session.strip()
    for session in os.getenv("SESSIONS", "").splitlines()
    if session.strip()
]

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
        "status": "online",
        "sessions_configured": len(SESSIONS)
    })

@app.route("/health")
def health():
    return jsonify({"status": "healthy"}), 200

# ---------------- TELEGRAM ----------------

clients = []

async def validate_session(index, session):
    client = None

    try:
        client = TelegramClient(
            StringSession(session),
            API_ID,
            API_HASH
        )

        await client.connect()

        if not await client.is_user_authorized():
            logger.warning("Account %s: Session is not authorized", index)
            return

        me = await client.get_me()

        logger.info(
            "Account %s: Connected successfully (%s)",
            index,
            me.first_name or "Telegram User"
        )

        clients.append(client)
        client = None

    except Exception as error:
        logger.error(
            "Account %s: Connection failed (%s)",
            index,
            type(error).__name__
        )

    finally:
        if client:
            try:
                await client.disconnect()
            except Exception:
                pass


async def telegram_manager():
    if not API_ID or not API_HASH:
        logger.error("API_ID or API_HASH is missing.")
        return

    if not SESSIONS:
        logger.error("No sessions found in SESSIONS environment variable.")
        return

    logger.info("Starting session validation...")
    logger.info("Total sessions configured: %s", len(SESSIONS))

    for index, session in enumerate(SESSIONS, start=1):
        await validate_session(index, session)

    logger.info(
        "Session validation finished. Connected accounts: %s",
        len(clients)
    )

    # Keep authorized clients connected.
    while True:
        await asyncio.sleep(60)


def start_telegram():
    try:
        asyncio.run(telegram_manager())
    except Exception as error:
        logger.error("Telegram manager stopped: %s", type(error).__name__)


# ---------------- START ----------------

if __name__ == "__main__":
    threading.Thread(
        target=start_telegram,
        daemon=True
    ).start()

    logger.info("SEM VC JOINER web server starting...")
    app.run(
        host="0.0.0.0",
        port=PORT,
        use_reloader=False
    )
