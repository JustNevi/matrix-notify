import os
import asyncio
import json
import logging

from nio import AsyncClient, LoginResponse, InviteEvent, MatrixRoom

class MatrixClient(AsyncClient):
    def __init__(self, homeserver, user_id, config_path="", store_path="", do_logging=False):
        super().__init__(
            homeserver,
            user=user_id,
            store_path=store_path,
        )

        self.config_path = config_path 

        # Logger setup
        self._logger = None
        if (do_logging):
            self._setup_logger()

        self._load_config()

        self._is_logged = False
       
        # Events
        # handle room invites
        self.join_event = asyncio.Event()
        self.add_event_callback(self.room_invite_callback, InviteEvent)


    # If no config has been loaded, the password will be used to log in.
    async def login(self, password=""):
        if (self.access_token == ""):
            if (password == ""):
                raise Exception("If config is not used, you must provide a password to log in.")

            resp = await super().login(password)
            
            # Check that we logged in successfully
            if isinstance(resp, LoginResponse):
                self.log("info", "Logged in successfully.")
                self._store_config(resp, self.homeserver)
                self._is_logged = True
            else:
                self.log("error", f"Failed to log in: {resp}")
                self._is_logged = False
        else:
            # This loads verified/blacklisted devices and keys.
            # Required to send encrypted messages.
            super().load_store()
            self._is_logged = True
            self.log("info", "Logged in using stored credentials.")

    # Decorator to check loggin status and log in automatically if using saved credentials
    def _loggedin(func):
        async def wrapper(self, *args, **kwargs):
            if (not self._is_logged):
                await self.login()
            # Check if logged was successfull again
            if (self._is_logged):
                return await func(self, *args, **kwargs)
            else:
                raise Exception("Cannot be completed because login is not possible.")
        return wrapper

    async def room_invite_callback(self, room: MatrixRoom, event: InviteEvent):
        await self.join(room.room_id)
        self.log("info", f"Room {room.name} is encrypted: {room.encrypted}")
        self.join_event.set() # Signal that the join is complete

    # Decorator that ensures the client is in a specific room before executing a function.
    def _in_room(func):
        async def wrapper(self, room_id, *args, **kwargs):
            if room_id not in self.rooms:
                self.log("info", f"Room {room_id} not in known rooms. Waiting for invite.")
                try:
                    # Wait for the join event with a timeout
                    await asyncio.wait_for(self.join_event.wait(), timeout=10)
                    self.log("info", "Room join event was set.")

                    # Update sync for new room
                    await asyncio.sleep(5)
                    await self.sync(timeout=30000, full_state=True)
                except asyncio.TimeoutError:
                    self.log("error", "Timed out waiting for room invite.")
                    raise Exception("Cannot send message: Room was not joined within the timeout.")
            
            # Reset the event for the next invite
            self.join_event.clear()
            
            return await func(self, room_id, *args, **kwargs)
        return wrapper

    @_loggedin
    @_in_room
    async def send_simple_message(self, room_id, message):
        await super().room_send(
            room_id,
            message_type="m.room.message",
            content={
                "msgtype": "m.text", 
                "body": message
            },
            ############################
            # Ignore untrusted devices #
            ############################
            ignore_unverified_devices=True
        )
        self.log("info", f"Message has been sent: {message}")


    # If config file exists, load all session credentials
    # to not use password again
    def _load_config(self):
        if (os.path.exists(self.config_path)):
            try:
                # Get config from file
                with open(self.config_path) as f:
                    content = f.read()
                config = json.loads(content)
                
                # Load config variables
                self.homeserver = config.get("homeserver", self.homeserver)
                self.user_id = config.get("user_id", self.user_id)
                self.device_id = config.get("device_id", "")
                self.access_token = config.get("access_token", "")
            except Exception as e:
                self.log("error", f"Config load error: {e}")
                raise Exception("Config load error")

    # Store login credentials from login responseonse 
    def _store_config(self, response, homeserver):
        if (os.path.exists(self.config_path)):
            with open(self.config_path, "w") as f:
                json.dump(
                    {
                        "homeserver": homeserver,
                        "user_id": response.user_id,
                        "device_id": response.device_id,
                        "access_token": response.access_token,
                    },
                    f,
                )
         

    def log(self, level, message):
        if (self._logger):
            level_map = {
                "debug": self._logger.debug,
                "info": self._logger.info,
                "warning": self._logger.warning,
                "error": self._logger.error,
                "critical": self._logger.critical,
            }
            level_map[level.lower()](message) 


    def _setup_logger(self):
        self._logger = logging.getLogger(__name__)
