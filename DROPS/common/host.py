from dataclasses import dataclass


@dataclass(frozen=True,slots=True)
class HostInfo:
    host: str
    port: int

    def __str__(self):
        return f"{self.host}:{self.port}"

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return self.host == other.host and self.port == other.port

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.host, self.port))

    @staticmethod
    def from_string(host_port: str):
        host, port = host_port.split(":")
        return HostInfo(host, int(port))

    @staticmethod
    def from_tuple(host_port: tuple):
        host, port = host_port
        return HostInfo(host, int(port))

    def to_tuple(self):
        return (self.host, self.port)

    def to_string(self):
        return f"{self.host}:{self.port}"
    
    def to_dict(self):
        return {'host': self.host, 'port': self.port}