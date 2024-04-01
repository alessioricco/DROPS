from typing import Set
from sortedcontainers import SortedDict
import hashlib

class HashRing:
    def __init__(self, nodes=None):
        # Convert nodes to a set to ensure compatibility with add and remove methods
        self.nodes = set(nodes) if nodes else set()
        self.ring = SortedDict()
        for node in self.nodes:
            self.add_node(node)

    def add_node(self, node_identifier:str):
        hash_val = self._hash(node_identifier)
        self.nodes.add(node_identifier)
        self.ring[hash_val] = node_identifier

    def remove_node(self, node_identifier:str):
        if node_identifier in self.nodes:
            hash_val = self._hash(node_identifier)
            self.nodes.remove(node_identifier)
            if hash_val in self.ring:
                del self.ring[hash_val]

    def get_node(self, key:str):
        if not self.ring:
            return None
        hash_val = self._hash(key)
        # Get all hashes greater than or equal to the key's hash
        greater_hashes = [h for h in self.ring.keys() if h >= hash_val]
        # If no greater hash is found, wrap around to the first hash in the ring
        nearest_hash = greater_hashes[0] if greater_hashes else next(iter(self.ring))
        return self.ring[nearest_hash]

    def _hash(self, key:str):
        """A simple hashing function."""
        return int(hashlib.sha256(key.encode('utf-8')).hexdigest(), 16) % 1000000
