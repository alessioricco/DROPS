import json

from DROPS.common.MessageEnvelope import MessageEnvelope
from .Command import Command
from DROPS.common.logtools import logger

class CommandNodeCacheSet(Command):
    
    # def __init__(self, node):
    #     self.node = node
        
    async def execute(self, message:dict, writer):
        key = message['key']
        value = message['value']
        responsible_node = self.node.hash_ring.get_node(key)
        if responsible_node == self.node.node_identifier:
            # This node is responsible for the key
            self.node.cache.set(key, value)
            # response = {'status': 'success', 'action': 'set', 'key': key}
            # writer.write(json.dumps(response).encode())
            # await writer.drain()
            success_message = {'status': 'success', 'action': 'set', 'key': key}
            response:MessageEnvelope = self.node.messageBuilder.buildMessageSuccess(success_message)
            response.send(writer)
            return
        
        # Forward the request to the responsible node
        logger.info(f"set {key} request but i'm not responsible: {responsible_node}")