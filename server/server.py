import asyncio
from .authentication import AuthenticationManager
from .broadcast import BroadcastManager

class ChatServer:
    def __init__(self, host='127.0.0.1', port=12345):
        self.host = host
        self.port = port
        self.authentication_manager = AuthenticationManager()
        self.broadcast_manager = BroadcastManager()

    async def handle_client(self, reader, writer):
        # Ask if the user wants to register or login
        writer.write(b"Do you want to [r]egister or [l]ogin? ")
        await writer.drain()

        action = await reader.readuntil(b'\n')
        action = action.decode().strip().lower()

        if action == 'r':
            await self.register_new_user(reader, writer)
        elif action == 'l':
            await self.login_user(reader, writer)
        else:
            writer.write(b"Invalid action. Please choose 'r' to register or 'l' to login.\n")
            await writer.drain()
            writer.close()
            await writer.wait_closed()

    async def register_new_user(self, reader, writer):
        """Handle new user registration."""
        writer.write(b"Enter your desired username: ")
        await writer.drain()
        username = await reader.readuntil(b'\n')
        username = username.decode().strip()

        writer.write(b"Enter your password: ")
        await writer.drain()
        password = await reader.readuntil(b'\n')
        password = password.decode().strip()

        try:
            self.authentication_manager.register_user(username, password)
            writer.write(b"Registration successful! You can now log in.\n")
            await writer.drain()
        except ValueError as e:
            writer.write(f"Error: {e}\n".encode())
            await writer.drain()

        writer.close()
        await writer.wait_closed()

        self.authentication_manager.save_to_file()

    async def login_user(self, reader, writer):
        """Handle user login."""
        writer.write(b"Enter your username: ")
        await writer.drain()
        username = await reader.readuntil(b'\n')
        username = username.decode().strip()

        writer.write(b"Enter your password: ")
        await writer.drain()
        password = await reader.readuntil(b'\n')
        password = password.decode().strip()

        if self.authentication_manager.authenticate(username, password):
            writer.write(b"Login successful! Welcome to the chat.\n")
            await self.broadcast_manager.broadcast_message(f"{username} has joined the chat.", exclude=username)
            await writer.drain()

            # Add the user to the broadcast system
            self.broadcast_manager.add_client(username, writer)

            # Start chat interaction
            await self.chat_with_user(reader, writer, username)
        else:
            writer.write(b"Authentication failed. Please try again.\n")
            await writer.drain()

        writer.close()
        await writer.wait_closed()

    async def chat_with_user(self, reader, writer, username):
        """Handle the chat interaction after login."""
        try:
            while True:
                # Read a message from the user
                writer.write(b"Type your message (or 'exit' to quit): ")
                await writer.drain()
                data = await reader.readuntil(b'\n')
                message = data.decode().strip()

                if message.lower() == 'exit':
                    writer.write(b"Goodbye!\n")
                    await writer.drain()
                    break

                # Broadcast the message to other users
                await self.broadcast_manager.broadcast_message(f"{username}: {message}", exclude=username)
        except Exception as e:
            print(f"Error with user {username}: {e}")
        finally:
            # Clean up when the user disconnects
            self.broadcast_manager.remove_client(username)
            writer.close()
            await writer.wait_closed()

    async def run(self):
        server = await asyncio.start_server(self.handle_client, self.host, self.port)
        print(f"Chat server running on {self.host}:{self.port}")
        async with server:
            await server.serve_forever()
