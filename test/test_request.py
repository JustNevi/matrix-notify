import requests

ip = "0.0.0.0"
port = "8000"

data = {"message": "Test message"}
response = requests.post(f"http://{ip}:{port}/", json=data)
print(response.json())
