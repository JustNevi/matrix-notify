import requests

from dotenv import load_dotenv
load_dotenv()

SERVER_IP = os.getenv("SERVER_IP")
SERVER_PORT = os.getenv("SERVER_PORT")

ROOM_ID = os.getenv("ROOM_ID")
TEST_MESSAGE = os.getenv("TEST_MESSAGE")

data = {
    "room_id": ROOM_ID, 
    "message": TEST_MESSAGE
}

response = requests.post(f"http://{SERVER_IP}:{SERVER_PORT}/", json=data)
print(response.json())
