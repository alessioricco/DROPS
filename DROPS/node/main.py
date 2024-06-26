import ssl
import asyncio
import json

from DROPS.common.host import HostInfo


from .DistributedNode import DistributedNode
from DROPS.common.configtools import read_config_file
from DROPS.common.logtools import logger

def main():
    
    config_file:str = './node.yaml'
    
    try:
        config = read_config_file(config_file)
    except FileNotFoundError:
        logger.error(f"Configuration file '{config_file}' not found.")
        return
    except json.JSONDecodeError:
        logger.error(f"Configuration file '{config_file}' contains invalid JSON.")
        return
    
    # SSL context creation for demonstration; replace paths with actual certificate and key file paths
    ssl_context = None
    if config['security']['tls_enabled']:
        ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        ssl_context.load_cert_chain(certfile=config['security']['tls_cert_path'], keyfile=config['security']['tls_key_path'])
    
    directory_nodes = set([(elem['host'], elem['port']) for elem in config['directory_services']])
    node = DistributedNode(HostInfo(config['node']['host'], config['node']['port']), directory_nodes, ssl_context=ssl_context)
    asyncio.run(node.start())

if __name__ == '__main__':
    main()