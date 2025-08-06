# Usage

## Docker

### Build

```
docker build -t matrix-notify . # or any tag you want
```

### Run

```
docker run -d --rm --env-file .env -p 8000:8000 matrix-notify:latest
```

# Examples

`.env` file:

```
BACKUP_PATH=../files/backup/

HOMESERVER=https://matrix.example.org
USER_ID=example_user_id
USER_PASS=super-password-123

ROOM_ID=!sdDSfjasdflkjTESTROOM:matrix.example.org

```

# Notes

## Backup

Create `config.json` file and `store/` directory in yours `BACKUP_PATH` before running. The program does not create them automatically.

You can pay attention to this in `Dockerfile`:

```Dockerfile
#.....
# Create app user and working directory
RUN useradd -m -r appuser \
	 && mkdir /opt/matrix-notify/ \
	 # Create directory and files for saving matrix client credentials, keys ets.
	 && mkdir -p /opt/matrix-notify/files/backup/store \
	 && touch /opt/matrix-notify/files/backup/config.json \
	 && echo "{}" > /opt/matrix-notify/files/backup/config.json \
	 # Assign a directory to a user
	 && chown -R appuser /opt/matrix-notify/
#.....
```

## E2EE

By default nio does not have end-to-end encryption support. For e2ee support, python-olm is needed which requires the libolm C library (version 3.x).

After libolm has been installed, the e2ee enabled version of nio can be installed using pip:

```
pip install matrix-nio[e2e]
```
