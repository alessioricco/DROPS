from DROPS.common.logtools import logger
from DROPS.common.MessageEnvelope import MessageEnvelope, MessageType
from DROPS.common.timetools import time_execution
from .Command import Command
from .CommandNodeRegister import CommandNodeRegister
from .CommandNodeDiscover import CommandNodeDiscover
from .CommandNodeCacheSet import CommandNodeCacheSet
from .CommandClientCacheSet import CommandClientCacheSet

class Dispatcher:
    
    __slots__ = ['node', 'command_handlers']
    
    def __init__(self, node):
        self.node = node
        
        self.command_handlers = {MessageType.NODE.value:
                                        {
                                            'register': CommandNodeRegister(self.node),
                                            'discover': CommandNodeDiscover(self.node),
                                            'set'     : CommandNodeCacheSet(self.node),
                                            # Add new commands here
                                        },
                                MessageType.CLIENT.value:
                                        {
                                            # Add client commands here
                                            'set'     : CommandClientCacheSet(self.node),
                                        }
                                }
    
    # @time_execution
    async def dispatch(self, envelope: MessageEnvelope, writer):
        try:
            command:str = envelope.command
            message_type:MessageType = envelope.message_type

            commandToExecute:Command = self.command_handlers.get(message_type.value, {}).get(command)
            if commandToExecute:
                logger.info(f"Received: {message_type}: {command}")
                await commandToExecute.execute(envelope.message, writer)
                return 
                
            logger.error(f"Unknown command received: {command}")  

        except Exception as e:
            logger.error(f"Error handling command: {e}", exc_info=True)
            



