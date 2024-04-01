import json

from DROPS.common.MessageEnvelope import MessageBuilder, MessageEnvelope
from .Command import Command

class CommandNodeDiscover(Command):
        
        async def execute(self, message:dict, writer):
            response:MessageEnvelope = self.node.messageBuilder.buildMessageNodeList(self.node.known_nodes)
            await response.send(writer)
            # await writer.drain()