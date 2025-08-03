import requests

ip = "127.0.0.1"
port = "8000"

data = {"message": "Test message"}
response = requests.post(f"http://{ip}:{port}/", json=data)
print(response.json())
