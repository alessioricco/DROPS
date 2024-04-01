import json
from .Command import Command

class CommandNodeDiscover(Command):
        
        async def execute(self, message:dict, writer):
            response = {'nodes': list(self.node.known_nodes)}
            writer.write(json.dumps(response).encode())
            await writer.drain()