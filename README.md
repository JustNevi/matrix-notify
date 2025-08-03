# Usage

## Request

```python
import requests

data = {"message": "Test message"}
response = requests.post("http://ip:port/", json=data)
```

# Examples

`.env` file:

```
BACKUP_PATH="../files/backup/"

HOMESERVER="https://matrix.example.org"
USER_ID="example_user_id"
USER_PASS="super-password-123"

ROOM_ID="!sdDSfjasdflkjTESTROOM:matrix.example.org"
MESSAGE="Test message!"

```

# Notes

## Backup

Create `config.json` file and `store/` directory in yours `BACKUP_PATH` before running. The program does not create them automatically.

## E2EE

By default nio does not have end-to-end encryption support. For e2ee support, python-olm is needed which requires the libolm C library (version 3.x).

After libolm has been installed, the e2ee enabled version of nio can be installed using pip:

```
pip install matrix-nio[e2e]
```
