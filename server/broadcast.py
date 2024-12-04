import asyncio
from typing import Dict


class BroadcastManager:
    def __init__(self):
        self.clients: Dict[str, asyncio.StreamWriter] = {}

    def add_client(self, username: str, writer: asyncio.StreamWriter):
        self.clients[username] = writer

    def remove_client(self, username: str):
        if username in self.clients:
            del self.clients[username]

    async def broadcast_message(self, message: str, exclude: str = None):   
        # Broadcast the message to all clients
        for username, writer in self.clients.items():
            if username != exclude:
                writer.write(f"\r{message}\n".encode())
                await writer.drain()

    async def send_private_message(self, message: str, recipient: str):
        if recipient in self.clients:
            writer = self.clients[recipient]
            writer.write(f"{message}\n".encode())
            await writer.drain()
        else:
            print(f"Recipient {recipient} not found")