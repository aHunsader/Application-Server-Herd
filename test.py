import asyncio
import time

servers = ["Goloman", "Hands", "Holiday", "Welsh", "Wilkes"]

ports = {
    "Goloman": 11580,
    "Hands": 11581,
    "Holiday": 11582,
    "Welsh": 11583,
    "Wilkes": 11584
}

async def test_server(loop):
    reader, writer = await asyncio.open_connection('127.0.0.1', port=ports["Hands"], loop=loop)
    writer.write("IAMAT kiwi.cs.ucla.edu +34.068930-118.445127 1520023934.918963997\n".encode())
    await writer.drain()
    data = await reader.readline()
    print(data.decode())
    writer.close()

    time.sleep(5)

    reader, writer = await asyncio.open_connection('127.0.0.1', port=ports["Hands"], loop=loop)
    writer.write("IAMAT kiwi.cs.ucla.edu +34.068930-118.445127 1510023934.918963997\n".encode())
    await writer.drain()
    data = await reader.readline()
    print(data.decode())
    writer.close()
    time.sleep(5)
    for server in servers:
        reader, writer = await asyncio.open_connection('127.0.0.1', port=ports[server], loop=loop)
        writer.write("WHATSAT kiwi.cs.ucla.edu 10 5\n".encode())
        await writer.drain()
        data = await reader.readline()
        print(server + ": ")
        print(data.decode())
        writer.close()

def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_server(loop))
    loop.close()


if __name__ == '__main__':
    main()