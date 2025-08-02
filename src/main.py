import os
import asyncio
import logging

from dotenv import load_dotenv

from matrix_client import MatrixClient

load_dotenv()

logging.basicConfig(level=logging.INFO)

# Env file variables
BACKUP_PATH = os.getenv("BACKUP_PATH")

HOMESERVER = os.getenv("HOMESERVER")
USER_ID = os.getenv("USER_ID")
USER_PASS = os.getenv("USER_PASS")

ROOM_ID = os.getenv("ROOM_ID")
MESSAGE = os.getenv("MESSAGE")

async def main():
    client = MatrixClient(
        homeserver=HOMESERVER, 
        user_id=USER_ID, 
        config_path=f"{BACKUP_PATH}/config.json",
        store_path=f"{BACKUP_PATH}/store/",
        do_logging=True
    )
    
    # Use full_state=True here to pull any room invites that occurred or
    # messages sent in rooms _before_ this program connected to the
    # Matrix server
    await client.sync(timeout=30000, full_state=True)

    await client.login(USER_PASS)

    await client.send_simple_message(ROOM_ID, MESSAGE)

    await client.close()

if (__name__ == "__main__"):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
