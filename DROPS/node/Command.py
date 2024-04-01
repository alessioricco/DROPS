import abc  # Abstract Base Classes

class Command(metaclass=abc.ABCMeta):
    
    def __init__(self, node):
        self.node = node
    
    @abc.abstractmethod
    async def execute(self, message:dict, writer):
        pass
    
