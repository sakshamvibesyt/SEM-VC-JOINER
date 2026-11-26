import asyncio
import logging
from telethon import TelegramClient
from config import API_ID, API_HASH, SESSIONS

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

async def main():
    clients = []

    for index, session in enumerate(SESSIONS, 1):
        session = session.strip()

        if not session:
            continue

        try:
            client = TelegramClient(
                StringSession(session),
                API_ID,
                API_HASH
            )

            await client.connect()

            if await client.is_user_authorized():
                clients.append(client)
                logging.info(f"Account {index}: Connected")
            else:
                logging.warning(f"Account {index}: Unauthorized")

        except Exception as e:
            logging.error(f"Account {index}: {e}")

    logging.info(f"Total connected: {len(clients)}")

    await asyncio.Event().wait()


if __name__ == "__main__":
    from telethon.sessions import StringSession
    asyncio.run(main())
