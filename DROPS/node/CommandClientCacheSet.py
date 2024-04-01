import json
from .Command import Command


class CommandClientCacheSet(Command):
    
    def __init__(self, node):
        self.node = node
        
    async def execute(self, message: dict, writer):
        key = message['key']
        value = message['value']
        responsible_node = self.node.hash_ring.get_node(key)
        
        if responsible_node == self.node.node_identifier:
            # This node is responsible for the key
            self.node.cache.set(key, value)
            response = {'status': 'success', 'action': 'set', 'key': key}
            writer.write(json.dumps(response).encode())
            await writer.drain()
        else:
            # Forward the request to the responsible node
            await self.node.forward_request(responsible_node, 'set', key, value)