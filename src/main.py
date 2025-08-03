import os
import asyncio
import logging

from matrix_client import MatrixClient

from flask import Flask, request, jsonify

# Load environment variables in development
try:
    from dotenv import load_dotenv
    load_dotenv()
except:
    pass


# Logging
logging.basicConfig(level=logging.INFO)


# Env file variables
BACKUP_PATH = os.getenv("BACKUP_PATH")

HOMESERVER = os.getenv("HOMESERVER")
USER_ID = os.getenv("USER_ID")
USER_PASS = os.getenv("USER_PASS")

ROOM_ID = os.getenv("ROOM_ID")


# Initialize Matrix client
client = MatrixClient(
    homeserver=HOMESERVER, 
    user_id=USER_ID, 
    config_path=f"{BACKUP_PATH}/config.json",
    store_path=f"{BACKUP_PATH}/store/",
    do_logging=True
)


async def main(message):
    # Use full_state=True here to pull any room invites that occurred or
    # messages sent in rooms _before_ this program connected to the
    # Matrix server
    await client.sync(timeout=30000, full_state=True)

    await client.login(USER_PASS)

    await client.send_simple_message(ROOM_ID, message)

    await client.close()


# Create app
app = Flask(__name__)

@app.route("/", methods=["POST"])
def index():
    try:
        # Get message
        message = request.get_json()["message"]

        # TODO: Use Celery instead
        asyncio.run(main(message))

        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": e})


if (__name__ == "__main__"):
    app.run(debug=True) 
