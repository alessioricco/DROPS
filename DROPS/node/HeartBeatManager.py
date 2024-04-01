import asyncio
import json
from DROPS.common.logtools import logger
from DROPS.common.MessageEnvelope import MessageEnvelope, _onMessageSend


class HeartBeatManager:
    
    def __init__(self, node):
        self.node = node
    
    async def send_heartbeat(self):
        for node in list(self.node.known_nodes):
            if node == (self.node.host, self.node.port):  # Skip self
                continue
            try:
                reader, writer = await asyncio.open_connection(node[0], node[1], ssl=self.ssl_context)
                # message:MessageEnvelope = buildMessageHeartbeat(self.node.node_identifier)
                message:MessageEnvelope = self.node.messageBuilder.buildMessageHeartbeat()
                # writer.write(json.dumps({'command': 'heartbeat'}).encode())
                writer.write(_onMessageSend(message))
                await writer.drain()
                writer.close()
            except Exception as e:
                logger.error(f"Failed to send heartbeat to {node[0]}:{node[1]}: {e}")
                self.known_nodes.remove(node)

    async def heartbeat_scheduler(self):
        """
        Periodically sends heartbeats to all known nodes to maintain the network and clean up inactive nodes.
        """
        while True:
            await self.send_heartbeat()  # Send initial heartbeat immediately
            await asyncio.sleep(300)  # Wait for 5 minutes before sending the next heartbeat

