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



import asyncio
import logging
from websockets import WebSocketServerProtocol
from websockets import WebSocketClientProtocol
from pyscat.serial.device_serial import DeviceSerialConnection
from pyscat.serial.serial_discover import SerialAutoDiscover
from pyscat.serial.serial_health import SerialHealthCheck

logging.basicConfig(level=logging.INFO)


# Only one websocket server for all devices
class WebSocketServer:
    # web socket slot mapping
    slot_socket_map = {}
    # web socket to serial device mapping
    slot_device_map = {}

    # register every serial device so that websocket server knows how to send commands recvd from clients
    async def register_device(self, slot: str, device: DeviceSerialConnection) -> None:
        self.slot_device_map[slot] = device
        logging.debug(self.slot_device_map)

    # register every websocket client to slot mapping
    async def register_socket(self, slot: str, ws: WebSocketServerProtocol) -> None:
        try:
            if not self.slot_device_map[slot]:
                raise ValueError("Invalid slot "+slot)
        except KeyError:
            raise ValueError("Invalid slot " + slot)

        if slot not in self.slot_socket_map or not self.slot_socket_map[slot]:
            self.slot_socket_map[slot] = set()

        self.slot_socket_map[slot].add(ws)
        logging.info(ws.remote_address)

    # unregister every websocket client to slot mapping
    async def unregister_socket(self, slot: str, ws: WebSocketServerProtocol) -> None:
        if self.slot_socket_map[slot]:
            self.slot_socket_map[slot].remove(ws)
        logging.info(ws.remote_address)

    # websocket callback when clients connect.
    async def ws_handler(self, ws: WebSocketServerProtocol, uri: str) -> None:
        slot = uri.strip("/")

        try:
            await self.register_socket(slot, ws)
            # register consumer to consume incoming messages
            await self.consume_handler(ws)
            try:
                await self.distribute(slot, "")
            finally:
                await self.unregister_socket(slot, ws)
        except Exception:
            # logger.error("Error in connection handler", exc_info=True)
            if not ws.closed:
                ws.fail_connection(1011)
            raise

    # get message from websocket and send to corresponding serial device
    async def consume_handler(self, websocket: WebSocketClientProtocol) -> None:
        async for message in websocket:
            if message == 'CATSAutoDiscover On':
                logging.info(message)
                serial_discover = SerialAutoDiscover()
                serial_discover.discover(self.slot_device_map)
            elif message == 'CATSAutoDiscover Off':
                logging.info(message)
                serial_discover = SerialAutoDiscover()
                serial_discover.discover_off(self.slot_device_map)
            elif message == 'CATSHealthReport':
                logging.info(message)
                serial_health = SerialHealthCheck()
                serial_health.report_health(self.slot_device_map)
            else:
                device = self.slot_device_map[websocket.path[1:]]
                await device.send_message(message)

    # send messages from http to  serial for slots
    async def send_to_serial(self, slot, message: str) -> None:
        device = self.slot_device_map[slot]
        await device.send_message(message)

    # send messages from http to  serial for slots
    async def send_hex_to_serial(self, slot, message: str) -> None:
        device = self.slot_device_map[slot]
        await device.send_hex_message(message)

    async def send_binary_to_serial(self, slot, message: str) -> None:
        device = self.slot_device_map[slot]
        await device.send_binary_message(message)

    # send messages from serial device to websocket client for slots
    async def distribute(self, slot, message: str) -> None:
        if slot in self.slot_socket_map and self.slot_socket_map[slot]:
            await asyncio.wait([asyncio.create_task(client.send(message)) for client in self.slot_socket_map[slot]])
