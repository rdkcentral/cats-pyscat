# Copyright 2024 Comcast Cable Communications Management, LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# SPDX-License-Identifier: Apache-2.0



'''
Description:
    Examples for running pyscat client
'''
from time import sleep
import asyncio
from loguru import logger
from scatclient.gateway import PyscatClient
import sys
import getopt

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


def module_args(argv):
    arg_host = ""
    arg_slot = ""
    arg_port = 15080
    arg_component = 0
    arg_help = "{0} -host <host> -port <port> -slot <slot>  -component <component>".format(argv[0])
    
    try:
        opts, args = getopt.getopt(argv[1:], "hhost:port:slot:component:", ["help", "host=", 
        "port=", "slot=","component="])
    except:
        print(arg_help)
        sys.exit(2)
    
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print(arg_help)  # print the help message
            sys.exit(2)
        elif opt in ("-host", "--host"):
            arg_host = arg
        elif opt in ("-slot", "--slot"):
            arg_slot = arg
        elif opt in ("-component", "--component"):
            arg_component = arg
        elif opt in ("-port", "--port"):
            arg_port = arg

    return (arg_host,arg_port,arg_slot,arg_component)

if __name__ == "__main__":
    #default values
    # SOCKET_PORT = 15080
    # HOST = '0.0.0.0'
    # SLOT = 1
    # COMPONENT = 0
    HOST ,SOCKET_PORT,SLOT,COMPONENT =  module_args(sys.argv)
    
   
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


    logger.info("--- ASYNC FORMAT --- ")
    ws = client.create_connection()
    logger.info(f"Connection : {ws}")
    logger.info(f"WS State : { ws.state}")

    loop = asyncio.get_event_loop().run_until_complete(main())