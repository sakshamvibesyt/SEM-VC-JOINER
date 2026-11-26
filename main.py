
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
    s.strip()
    for s in os.getenv("SESSIONS", "").splitlines()
    if s.strip()
]

# ---------------- LOGGING ----------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

# ---------------- WEB SERVER ----------------

app = Flask(__name__)

@app.route("/")
def home():
    return jsonify({
        "project": "SEM VC JOINER",
        "status": "Running"
    })

@app.route("/health")
def health():
    return jsonify({"status": "healthy"}), 200

# ---------------- TELEGRAM MANAGER ----------------

clients = []

async def telegram_manager():

    if not API_ID or not API_HASH:
        logging.error("API_ID or API_HASH missing")
        return

    if not SESSIONS:
        logging.error("No sessions configured")
        return

    for index, session in enumerate(SESSIONS, start=1):

        client = TelegramClient(
            StringSession(session),
            API_ID,
            API_HASH
        )

        try:
            await client.connect()

            if await client.is_user_authorized():
                clients.append(client)
                logging.info(f"Account {index}: Connected")

            else:
                logging.warning(
                    f"Account {index}: Unauthorized session"
                )
                await client.disconnect()

        except Exception:
            logging.exception(f"Account {index}: Connection failed")

    logging.info(
        f"Connected accounts: {len(clients)}/{len(SESSIONS)}"
    )

    await asyncio.Event().wait()


def start_telegram():

    asyncio.run(telegram_manager())


if __name__ == "__main__":

    threading.Thread(
        target=start_telegram,
        daemon=True
    ).start()

    app.run(
        host="0.0.0.0",
        port=int(os.getenv("PORT", 10000))
    )
