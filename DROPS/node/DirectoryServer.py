import asyncio
import json
import ssl

class DirectoryServer:
    def __init__(self, host, port):
        self.active_nodes = {}  # Store node information
        self.host = host
        self.port = port

    async def handle_client(self, reader, writer):
        data = await reader.read(4096)
        message = json.loads(data.decode())
        command = message['command']
        node_info = message['node']

        if command == 'register':
            self.active_nodes[node_info['id']] = node_info
            response = {'status': 'registered', 'nodes': list(self.active_nodes.values())}
        elif command == 'discover':
            response = {'nodes': list(self.active_nodes.values())}
        
        writer.write(json.dumps(response).encode())
        await writer.drain()
        writer.close()

    async def run(self, ssl_context):
        server = await asyncio.start_server(
            self.handle_client, self.host, self.port, ssl=ssl_context)
        addr = server.sockets[0].getsockname()
        print(f'Serving on {addr}')

        async with server:
            await server.serve_forever()

    # async def run(self):
    #     server = await asyncio.start_server(self.handle_client, self.host, self.port)
    #     print(f"Directory service active on {self.host}:{self.port}")
    #     async with server:
    #         await server.serve_forever()

# To run the directory server
# directory_server = DirectoryServer('0.0.0.0', 1969)
# asyncio.run(directory_server.run())
