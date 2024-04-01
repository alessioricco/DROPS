import json
from .Command import Command


class CommandNodeRegister(Command):
    
    def __init__(self, node):
        self.node = node

    async def execute(self, message:dict, writer):

        self.node.known_nodes.add((message['host'], message['port']))
        response = {'status': 'registered', 'nodes': list(self.node.known_nodes)}
        writer.write(json.dumps(response).encode())
        await writer.drain()