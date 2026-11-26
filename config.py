import os

API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")

GROUP_ID = os.getenv("GROUP_ID", "")

SESSIONS = os.getenv("SESSIONS", "").split(",")
