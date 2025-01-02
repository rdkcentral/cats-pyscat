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
    Run Pytest for Pyscat Client
Command:
    pytest -v -s scatclient/tests/test_client.py
'''
from time import sleep
import os
import asyncio
from configparser import ConfigParser
import logging
import unittest
import pytest
import aiounittest
from scatclient.gateway import PyscatClient

logger = logging.getLogger(__name__)
dirname = os.path.dirname(__file__)


class PyscatClientTest(unittest.TestCase):
    '''
    Pyscat Client Test
    '''

    def setUp(self) -> None:
        config_object = ConfigParser()
        file_path = os.path.join(dirname + os.sep + "config.ini")
        config_object.read(file_path)
        setup_info = config_object["config"]
        host = setup_info["HOST"]
        port = setup_info["PORT"]
        slot = setup_info["SLOT"]
        component = setup_info["COMPONENT"]
        self.client = PyscatClient(
            host=host,
            slot=slot,
            port=port,
            component=component)

    @pytest.mark.order(1)
    def test_create_connection(self):
        '''Test create connection'''
        websocket = self.client.create_connection()
        status = websocket.state
        logger.info("Websocket State : %s", status)
        assert status == "State.OPEN"
        pytest.websocket = websocket

    @pytest.mark.order(2)
    def test_read_send(self):
        '''Test send and read through websocket '''
        websocket = pytest.websocket
        message_sent = "Hello World !!"
        logger.info("Sending message")
        websocket.send(message_sent)

        logger.info("Receiving message")
        message_recv = websocket.recv()
        logger.info("From Server : %s", message_recv)
        assert message_sent == message_recv

    @pytest.mark.order(3)
    def test_disconnect(self):
        '''Test disconnect'''
        websocket = pytest.websocket
        logger.info("Closing Connection")
        websocket.close()
        status = websocket.state
        assert 'State.CLOSED' == status
        logger.info("Websocket State : %s",status)


class PyscatAsyncTest(aiounittest.AsyncTestCase):
    '''Pyscat Client Asnc function test case'''

    def setUp(self) -> None:
        '''Set up test case'''
        config_object = ConfigParser()
        file_path = os.path.join(dirname + os.sep + "config.ini")
        config_object.read(file_path)
        setup_info = config_object["config"]
        host = setup_info["HOST"]
        port = setup_info["PORT"]
        slot = setup_info["SLOT"]
        component = setup_info["COMPONENT"]
        self.client = PyscatClient(
            host=host,
            slot=slot,
            port=port,
            component=component)
        self.disconnect_msg = "Disconnecting client"
        self.reader_msg = ''

    def get_event_loop(self):
        '''Event loop set to run async loop seperately'''
        self.my_loop = asyncio.get_event_loop()
        return self.my_loop

    @pytest.mark.order(5)
    def test_create_connection(self):
        '''Test create connection'''
        websocket = self.client.create_connection()
        status = websocket.state
        logger.info("WS State : %s", status)
        assert status == "State.OPEN"
        pytest.websocket = websocket

    async def track_reader(self, counter=10):
        '''Function to track the reader function read'''
        websocket = pytest.websocket
        while counter > -1:
            # await necessary to let free strict control
            await asyncio.sleep(1)
            if counter == 0:
                await websocket.write(self.disconnect_msg)
                sleep(1)
                await websocket.connection.close()
                logger.info("WS State : %s", websocket.state)

                break
            counter = counter - 1
        return websocket.state

    async def read(self):
        '''Read messages from websocket continuously'''
        websocket = pytest.websocket
        async for msg in websocket.read():
            self.reader_msg = msg
            await asyncio.sleep(1)

    @pytest.mark.order(6)
    async def test_main(self):
        '''Test read and read tracker functions'''
        ret = await asyncio.gather(
            self.track_reader(10),
            self.read()
        )
        assert 'State.CLOSED' == ret[0]
        assert self.reader_msg == self.disconnect_msg
