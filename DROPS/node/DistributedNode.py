import asyncio
import json
import ssl
import logging

from typing import List

from ..common.configtools import read_config_file
from ..common.logtools import logger
from ..common.MessageEnvelope import MessageEnvelope, MessageType, _encode_message_envelope, _decode_message_envelope, _onMessageSend, _onMessageReceive
from ..common.MessageEnvelope import MessageBuilder
from .HashRing import HashRing
from .DistributedCache import DistributedCache
from .HeartBeatManager import HeartBeatManager
from .Dispatcher import Dispatcher

class DistributedNode:

    def __init__(self, host:str, port:int, directory_nodes:set, ssl_context=None):
        self.node_info = {'host': host, 'port': port}
        self.host = host
        self.port = port
        self.ssl_context = ssl_context  # SSL context for secure communication
        self.directory_nodes = directory_nodes  # List of directory nodes
        self.known_nodes = set([(host, port)])  # Starts with itself known
        
        self.node_identifier = f"{host}:{port}"
        self.hash_ring = HashRing(nodes=[self.node_identifier])

        self.cache = DistributedCache(self.hash_ring)  # If your cache system is ready to use
        self.heartbeat_manager = HeartBeatManager(self)
        self.dispatcher = Dispatcher(self)
        self.messageBuilder = MessageBuilder(self.node_identifier)

    async def handle_client(self, reader, writer):
        """
        Handles incoming connections and processes the messages based on their type (peer or client).

        Args:
            reader: A StreamReader object for reading data from the connection.
            writer: A StreamWriter object for writing data to the connection.

        Returns:
            None
        """
        message_envelope:MessageEnvelope = _onMessageReceive(await reader.read(4096))
        await self.dispatcher.dispatch(message_envelope, writer)
        
        writer.close()  # Close the writer after handling the message

    async def forward_request(self, node_identifier, action, key, value=None):
        # Assuming node_identifier format is "host:port"
        host, port = node_identifier.split(':')
        
        try:
            # Use SSL if your system is designed to require it
            reader, writer = await asyncio.open_connection(host, int(port), ssl=self.ssl_context)

            # Construct and send the request
            # request = {
            #     "type": "node",  # Assuming you differentiate message types
            #     "action": action,
            #     "key": key
            # }
            
            request:MessageEnvelope = MessageEnvelope(message_type = MessageType.NODE, command = action, sender = self.node_identifier, message = {"key": key, "value":value})
            
            # if value is not None:
            #     request["value"] = value

            # writer.write(json.dumps(request).encode())
            writer.write(_onMessageSend(request))
            await writer.drain()

            # Optionally wait for and process the response
            # Depending on whether you expect/require a response for a forwarded request
            # response_data = await reader.read(4096)
            # response:MessageEnvelope = decode_message_envelope(response_data.decode())
            response:MessageEnvelope = _onMessageReceive(await reader.read(4096))
            # response = json.loads(response_data.decode())
            logger.info(f"Received response from {node_identifier}: {response}")

            writer.close()
            await writer.wait_closed()
        except Exception as e:
            logger.error(f"Failed to forward request to {node_identifier}: {e}", exc_info=True)

    async def handle_node_join(self, node_identifier, writer):
        self.hash_ring.add_node(node_identifier)
        # Logic to redistribute keys if necessary, acknowledge the node...

    async def handle_node_leave(self, node_identifier, writer):
        self.hash_ring.remove_node(node_identifier)
        # Logic to handle key redistribution, acknowledge the node's departure...

    def replicate_data(self, key, value):
        # Find the next N nodes in the hash ring for replication
        # Send set requests to these nodes
        pass

    async def contact_directory(self):
        while True:
            for directory_node in self.directory_nodes:
                directory_host, directory_port = directory_node
                try:
                    # Using self.ssl_context for secure connection
                    reader, writer = await asyncio.open_connection(
                        directory_host, directory_port, ssl=self.ssl_context)
                    # The rest of the method remains the same...
                    return  # Exit the loop if a connection is made
                except ConnectionRefusedError as e:
                    logger.error(f"Failed to contact directory node {directory_host}:{directory_port}")
                except Exception as e:
                    logger.error(f"Exception connecting {directory_host}:{directory_port}: {e}", exc_info=True)
            else:
                # Wait for 10 seconds if no connection is made
                await asyncio.sleep(10)

    async def start(self):
        server = await asyncio.start_server(
            self.handle_client, self.host, self.port, ssl=self.ssl_context)
        
        logger.info(f"Node service active on {self.host}:{self.port}")

        # Start the heartbeat scheduler as a background task
        asyncio.create_task(self.heartbeat_manager.heartbeat_scheduler())
    
        # Attempt to contact the directory service
        await self.contact_directory()

        async with server:
            await server.serve_forever()


