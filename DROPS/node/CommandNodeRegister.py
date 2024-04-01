import json

from DROPS.common.MessageEnvelope import MessageBuilder, MessageEnvelope
from .Command import Command


class CommandNodeRegister(Command):
    
    # def __init__(self, node):
    #     super().__init__(node)

    async def execute(self, message: dict, writer):
        self.node.known_nodes.add((message['host'], message['port']))
        response: MessageEnvelope = self.node.messageBuilder.buildMessageNodeList(self.node.known_nodes)
        await response.send(writer)
        # await writer.drain()
