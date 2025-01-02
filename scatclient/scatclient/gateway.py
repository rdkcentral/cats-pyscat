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



"""Interface to websocket client module
"""
import enum
import asyncio
from loguru import logger
from websockets.exceptions import WebSocketException , ConnectionClosed
from scatclient.wsclient import WebsocketClient


SOCKET_PORT = 15080


class State(enum.IntEnum):
    '''
    States of WebSocketClient protocol
    '''
    CONNECTING, OPEN, CLOSING, CLOSED, UNKNOWN = range(5)


class PyscatClient:
    '''
    Pyscat Websocket Client Interacting with Pyscat websocket server
    '''

    def __init__(self, host:str=None, port:int=None, slot:int=None, component:int=0):
        '''
        Arguments
        ---
        host {str}: The host of the websocket client
        port {int}: The port of websocket client
        slot {int}: The slot of the device
        component {int}: The component type of the device
        '''
        self.slot = slot
        self.host = host
        self.component = component
        self.hex = f"{int(self.component):08x}".upper() + f"{int(self.slot):04x}".upper()
        if port is None:
            self.port = SOCKET_PORT
        else:
            self.port = port
        self._ws_uri = f'ws://{self.host}:{self.port}/{self.hex}'
        self.socket_client = WebsocketClient(self._ws_uri)
        self.reader = None
        self.connection = None

    def create_connection(self):
        """Creates a connection to websocket
        """
        result = [str(State(4)),None]
        try:
            result = asyncio.get_event_loop().run_until_complete(self.socket_client.connect())
            if len(result) > 0:
                self.connection = result[1]
        except ConnectionClosed as exception:
            logger.exception(exception)
        return self

    def close(self):
        """Closes the websocket connection
        """
        try:
            asyncio.get_event_loop().run_until_complete(self.socket_client.close())
        except WebSocketException as exception:
            logger.exception(exception)

    @property
    def state(self):
        """Gets the state of websocket connection
        """
        try:
            state = str(State(self.socket_client.state))
        except Exception as exception:
            state = str(State(4))
            logger.exception(exception)
        return state

    def send(self, msg):
        """Sends a message to webSocket server

        Arguments:
        ----
        message {str} -- Data to send
        """
        try:
            asyncio.get_event_loop().run_until_complete(self.socket_client.send(msg))
        except Exception as exception:
            logger.exception(exception)

    def recv(self):
        """Receives messages
        """
        message = None
        try:
            message = asyncio.get_event_loop().run_until_complete(self.socket_client.receive())
        except Exception as exception:
            logger.exception(exception)
        return message

    async def write(self, msg):
        """Gets the state of websocket connection

        Arguments:
        ----
        message {str} -- Data to send
        """
        try:
            await self.socket_client.send(msg)
        except Exception as exception:
            logger.exception(exception)

    def read(self):
        """Reads the messages from websocket server
        """
        self.reader = self.socket_client.reader()
        return self.reader
