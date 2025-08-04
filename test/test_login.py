import nio
import asyncio

HOMESERVER = "https://localhost:8443"
USER_ID = "user"
USER_PASS = "user"


# Create a new homeserver client with SSL verification disabled
client = nio.AsyncClient(HOMESERVER, USER_ID, ssl=False)

async def main():
    # Now, try to login
    try:
        response = await client.login(USER_PASS)
        # Handle successful login
        print("Login successful!")
    except nio.exceptions.LocalProtocolError as e:
        # Handle failed login (e.g., incorrect credentials)
        print(f"Login failed: {e}")
    except Exception as e:
        # Handle other potential errors
        print(f"An error occurred: {e}")

if (__name__ == "__main__"):
    asyncio.run(main())
