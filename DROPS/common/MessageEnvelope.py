from asyncio import StreamReader, StreamWriter
import dataclasses
from datetime import datetime
import json
from enum import Enum
from typing import Optional

from DROPS.common.host import HostInfo
from .timetools import now
from enum import Enum

class MessageType(Enum):
    CLIENT = "client"
    NODE = "node"

@dataclasses.dataclass(slots=True, frozen=True)
class MessageEnvelope:
    message_type: MessageType = MessageType.CLIENT
    command: Optional[str] = None
    sender: Optional[str] = None
    timestamp: datetime = dataclasses.field(default_factory=now)
    message: dict = dataclasses.field(default_factory=dict)

    async def send(self, writer:StreamWriter):
        writer.write(_onMessageSend(self))
        await writer.drain()

    # def _send(self) -> bytes:
    #     return _onMessageSend(self)
    
    @staticmethod
    async def receive(reader:StreamReader, chunk_size:int=4096):
        data:bytes = await reader.read(chunk_size)
        return _onMessageReceive(data)
    
    # @staticmethod
    # def _receive(data:bytes):
    #     return _onMessageReceive(data)

def _onMessageSend(request:MessageEnvelope) -> bytes:
    
    def _encode_message_envelope(envelope: MessageEnvelope) -> str:
        envelope_dict = dataclasses.asdict(envelope)
        envelope_dict['message_type'] = envelope.message_type.value
        envelope_dict['timestamp'] = envelope.timestamp.isoformat()
        return json.dumps(envelope_dict)    
    
    return _encode_message_envelope(request).encode()

def _onMessageReceive(data:bytes) -> MessageEnvelope:

    def _decode_message_envelope(json_str: str) -> MessageEnvelope:
        envelope_dict = json.loads(json_str)
        envelope_dict['message_type'] = MessageType(envelope_dict['message_type'])
        envelope_dict['timestamp'] = datetime.fromisoformat(envelope_dict['timestamp'])
        return MessageEnvelope(**envelope_dict)

    return _decode_message_envelope(data.decode())

# ----------------- Example Usage -----------------
# Messaes as Derived Classes or not?
# for now not, for simplicity and efficiency (we want to be low latency)

class MessageBuilder:
    def __init__(self, sender:str):
        self.sender = sender

    def buildMessageHeartBeat(self) -> MessageEnvelope:
        return MessageEnvelope(message_type=MessageType.NODE, command="heartbeat", sender=self.sender)

    def buildMessageRegister(self, host_info:HostInfo) -> MessageEnvelope:
        message:dict = host_info.to_dict()
        return MessageEnvelope(message_type=MessageType.NODE, command="register", sender=self.sender, message=message)

    def buildMessageDiscover(self) -> MessageEnvelope:
        return MessageEnvelope(message_type=MessageType.NODE, command="discover", sender=self.sender)
    
    def buildMessageCacheSet(self, key:str, value:str) -> MessageEnvelope:
        message:dict = {"key": key, "value": value}
        return MessageEnvelope(message_type=MessageType.NODE, command="set", sender=self.sender, message=message)
    
    # def buildMessageCacheGet(self, key:str) -> MessageEnvelope:
    #     message:dict = {"key": key}
    #     return MessageEnvelope(message_type=MessageType.NODE, command="get", sender=self.sender, message=message)
    
    # def buildMessageCacheDelete(self, key:str) -> MessageEnvelope:
    #     message:dict = {"key": key}
    #     return MessageEnvelope(message_type=MessageType.NODE, command="delete", sender=self.sender, message=message)
    
    # def buildMessageCacheClear(self) -> MessageEnvelope:
    #     return MessageEnvelope(message_type=MessageType.NODE, command="clear", sender=self.sender)
    
    # def buildMessageCacheList(self) -> MessageEnvelope:
    #     return MessageEnvelope(message_type=MessageType.NODE, command="list", sender=self.sender)
    
    # def buildMessageCacheCount(self) -> MessageEnvelope:
    #     return MessageEnvelope(message_type=MessageType.NODE, command="count", sender=self.sender)
    
    def buildMessageNodeList(self, known_nodes) -> MessageEnvelope:
        return MessageEnvelope(message_type=MessageType.NODE, command="known_nodes", sender=self.sender, message={"nodes": list(known_nodes)})
    
    def buildMessageSuccess(self, message:dict={}) -> MessageEnvelope:
        return MessageEnvelope(message_type=MessageType.NODE, command="success", sender=self.sender, message=message)