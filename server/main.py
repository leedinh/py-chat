from .server import ChatServer

import asyncio


if __name__ == '__main__':
    server = ChatServer()
    asyncio.run(server.run())