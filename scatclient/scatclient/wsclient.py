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



"""Websocket Client Module"""
import asyncio
from websockets import WebSocketClientProtocol
from requests.exceptions import ConnectionError

import websockets
from loguru import logger


class WebsocketClient:
    """Websocket Client Class"""

    def __init__(self, uri,timeout=10,ping_interval=5):
        self.socket_client: WebSocketClientProtocol = None
        self.connected = False
        self.ws_url = uri
        self.ws_timeout = timeout
        self.ping_interval = ping_interval

    async def connect(self):
        """Creates a connection to websocket
        """
        try:
            self.socket_client = await websockets.connect(self.ws_url,open_timeout=self.ws_timeout,ping_interval=self.ping_interval)
            logger.info("Connection Established")
            return (self.socket_client.state, self.socket_client)
        except ConnectionError as exception:
            logger.exception(exception)


    @property
    def state(self):
        """Reads the state of the websocket connection
        """
        return self.socket_client.state

    async def close(self):
        """Close websocket"""
        await self.socket_client.close()

    async def send(self, message: str):
        """Sends a message to webSocket server

        Arguments:
        ----
        message {str} -- Data to send
        """
        await self.socket_client.send(message)

    async def receive(self):
        """Reads the message
        Arguments:
        ----
        disconnect {int} -- Waits for 10 sec and return the message.
        """
        message = await self.socket_client.recv()
        return message

    def reader(self):
        """Returns the websocket client protocol instance
        """
        return self.socket_client
