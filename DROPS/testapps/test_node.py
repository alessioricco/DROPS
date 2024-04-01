import asyncio
import ssl
from ..common.MessageEnvelope import MessageEnvelope, _onMessageSend, MessageBuilder

async def send_command(host, port, message:MessageEnvelope, use_ssl=False):
    """
    Connects to the server, sends a command, and prints the response.

    Args:
        host (str): The server's hostname or IP address.
        port (int): The server's port.
        message (dict): The message to send as a command to the server.
        use_ssl (bool): Whether to use SSL/TLS for the connection.
    """
    ssl_context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH) if use_ssl else None

    reader, writer = await asyncio.open_connection(host, port, ssl=ssl_context)
    print(f"Sending: {message}")
    
    writer.write(message.send())

    data = await reader.read(4096)
    print("Received:", MessageEnvelope.receive(data))

    writer.close()
    await writer.wait_closed()

async def main():
    host = '127.0.0.1'  # Server hostname or IP
    port = 1969         # Server port


    messageBuilder = MessageBuilder(host)

    register_command:MessageEnvelope = messageBuilder.buildMessageRegister("127.0.0.2", 1969)
    discover_command:MessageEnvelope = messageBuilder.buildMessageDiscover()

    # Use SSL/TLS if your server requires it
    use_ssl = False

    # Send register command
    await send_command(host, port, register_command, use_ssl)

    # Send discover command
    await send_command(host, port, discover_command, use_ssl)

if __name__ == '__main__':
    asyncio.run(main())
