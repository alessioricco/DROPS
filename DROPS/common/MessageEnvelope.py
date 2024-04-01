import dataclasses
from datetime import datetime
import json
from enum import Enum
from typing import Optional
from .now import now
from enum import Enum

class MessageType(Enum):
    CLIENT = "client"
    NODE = "node"

@dataclasses.dataclass
class MessageEnvelope:
    message_type: MessageType = MessageType.CLIENT
    command: Optional[str] = None
    sender: Optional[str] = None
    timestamp: datetime = dataclasses.field(default_factory=now)
    message: dict = dataclasses.field(default_factory=dict)

    def send(self) -> bytes:
        return _onMessageSend(self)
    
    @staticmethod
    def receive(data:bytes):
        return _onMessageReceive(data)

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

    def buildMessageHeartbeat(self) -> MessageEnvelope:
        return MessageEnvelope(message_type=MessageType.NODE, command="heartbeat", sender=self.sender)

    def buildMessageRegister(self, host:str, port:int) -> MessageEnvelope:
        message:dict = {"host": host, "port": port}
        return MessageEnvelope(message_type=MessageType.NODE, command="register", sender=self.sender, message=message)

    def buildMessageDiscover(self) -> MessageEnvelope:
        return MessageEnvelope(message_type=MessageType.NODE, command="discover", sender=self.sender)
    