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
CONFIG_PATH = os.path.join(BACKUP_PATH, "config.json")
STORE_PATH = os.path.join(BACKUP_PATH, "store")

HOMESERVER = os.getenv("HOMESERVER")
USER_ID = os.getenv("USER_ID")
USER_PASS = os.getenv("USER_PASS")


# Initialize Matrix client
client = MatrixClient(
    homeserver=HOMESERVER, 
    user_id=USER_ID, 
    config_path=CONFIG_PATH,
    store_path=STORE_PATH,
    do_logging=True
)

def setup():
    if not os.path.exists(BACKUP_PATH):
        os.makedirs(BACKUP_PATH)

    if not os.path.exists(STORE_PATH):
        os.makedirs(STORE_PATH)

    if not os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'w') as f:
            # Empty JSON object is crucial for python be able to load using "json" 
            f.write('{}')

async def main(room_id, message):
    await client.login(USER_PASS)

    # Use full_state=True here to pull any room invites that occurred or
    # messages sent in rooms _before_ this program connected to the
    # Matrix server
    await client.sync(timeout=30000, full_state=True)

    await client.send_simple_message(room_id, message)

    await client.close()


# Create app
app = Flask(__name__)

@app.route("/", methods=["POST"])
def index():
    try:
        setup()

        data = request.get_json()

        # Get message and room
        message = data.get("message")
        room_id = data.get("room_id")

        # TODO: Use Celery instead
        asyncio.run(main(room_id, message))

        return jsonify({"status": "success"})
    except Exception as e:
        async def client_close(): await client.close()
        asyncio.run(client_close())

        return jsonify({"status": "error", "message": str(e)})


if (__name__ == "__main__"):
    app.run(debug=True) 
