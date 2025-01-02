
# Functions

#### Import Pyscat Client
```
SOCKET_PORT = 15080
HOST = '0.0.0.0'
SLOT = 1
COMPONENT = 0

from scatclient.gateway import PyscatClient
client = PyscatClient(host = HOST,port = SOCKET_PORT , slot=SLOT,component=COMPONENT)
```

#### Create Connection and state of connection
```
ws = client.create_connection()
logger.info(f"Websocket State : {ws.state}")
```

#### Simple write and read
```
logger.info("Sending message")
ws.send("Hello World !!")
logger.info("Receiving message")
message = ws.recv()
logger.info(f"From Server: {message}")
```

#### Async continuous reader
```
async for msg in ws.read():
    logger.info(f"From Server: {msg}")
    await asyncio.sleep(1)
```

#### Async write
```
await ws.write("Disconnecting client")
```

#### Disconnect
```
logger.info("Closing Connection")
ws.close()
logger.info(f"Websocket State : {ws.state}")

OR 

logger.info("Closing Connection")
await ws.connection.close()
logger.info(f"Websocket State : {ws.state}")
```

# Samples


#### Run an example from installation
```
provide host , port , slot and component of connected pyscat socket and device. 

>  python -m scatclient.example --host 0.0.0.0 --port 15080 --slot 1 --component 0
```

#### Sample Usage  1

```
from scatclient.gateway import PyscatClient

SOCKET_PORT = 15080
HOST = '0.0.0.0'
SLOT = 1
COMPONENT = 0
logger.info("--- SYNC FORMAT --- ")
client = PyscatClient(
    host=HOST,
    port=SOCKET_PORT,
    slot=SLOT,
    component=COMPONENT)
ws = client.create_connection()
logger.info(f"Websocket State : { ws.state}")


async def track_reader(counter=10):
    """Stop connection when counter == counter value"""
    while counter > -1:
        await asyncio.sleep(1)  # await necessary to let free strict control
        if counter == 0:
            await ws.write("Disconnecting client")
            sleep(1)
            await ws.connection.close()
            logger.info(f"WS State : { ws.state}")

            break
        counter = counter - 1
    return ws.state


async def read():
    """Continuous read"""
    async for msg in ws.read():
        print(msg)
        await asyncio.sleep(1)

# Consolidate all async
async def main():
    '''Aync gather functions'''
    ret = await asyncio.gather(
        track_reader(10),
        read()
    )
    logger.info(f"Gather data {ret}")

loop = asyncio.get_event_loop().run_until_complete(main())

```
#### Sample Usage  2
```

from scatclient.gateway import PyscatClient

SOCKET_PORT = 15080
HOST = '0.0.0.0'
SLOT = 1
COMPONENT = 0

logger.info("--- SYNC FORMAT --- ")
client = PyscatClient(
    host=HOST,
    port=SOCKET_PORT,
    slot=SLOT,
    component=COMPONENT)
ws = client.create_connection()
logger.info(f"Websocket State : { ws.state}")

logger.info("Sending message")
ws.send("Hello World !!")

logger.info("Receiving message")
message = ws.recv()
logger.info(f"From Server :{message}")

logger.info("Closing Connection")
ws.close()
logger.info(f"Websocket State : {ws.state}")

```

# Pytest
```
pytest -v -s client/tests/test_client.py
```



