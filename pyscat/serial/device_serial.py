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

from pyscat.config import Config
from pyscat.devices import Devices, Device
import time
import serial
from serial import Serial
import threading
import logging
from threading import Lock

from pyscat.log_config import LogConfig
from pyscat.serial.serial_properties import SCATLegacyDevicesMap, SerialProperties
import re
from websockets import ConnectionClosed


# Represents a serial connection to a serial device port
class DeviceSerialConnection:
    config = Config()
    lock = Lock()
    ser: Serial = None
    discover_mode: bool = False
    callback = None
    is_error: bool = False
    close_connection: bool = False

    def __init__(self, device: Device):
        self.device = device
        self.formatter = logging.Formatter('%(asctime)s: %(message)s')

    # Start serial connection on a seperate thread
    def connect_to_device(self, server):
        self.close_connection = False;
        new_loop = asyncio.new_event_loop()
        read_thread = threading.Thread(target=self.start_loop, args=(new_loop, server), daemon=False)
        read_thread.start()

    def close_connection_to_device(self):
        self.close_connection = True;

    def start_loop(self, loop, server):
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.read_from_serial_device(server))

    # Start a serial connection and wait for messages to arrive on teh serial port
    async def read_from_serial_device(self, server):
        properties = self.get_properties()
        logger = LogConfig.setup_logger(self.device['id'],
                                        self.config.devices_config.trace_log_base + "/" + self.device['id'] + ".log")
        error_logger = LogConfig.setup_logger(self.device['id']+'-error',
                                              self.config.devices_config.trace_log_base + "/"
                                              + self.device['id'] + '-error' + ".log")
        system_logger = logging.getLogger('system')

        await server.register_device(self.device['id'], self)
        while not self.close_connection:
            try:
                self.ser = serial.Serial(port=self.device['connectionProperties']['port'],
                                         baudrate=properties.baud,
                                         stopbits=properties.stop_bits,
                                         parity=properties.parity,
                                         bytesize=properties.data_bits,
                                         timeout=1)

                while not self.close_connection:
                    try:
                        # data = ser.read_until('/r/n')
                        data = self.ser.readline()
                        if data:
                            if self.discover_mode:
                                message = data.decode('utf-8').rstrip()
                                p = re.compile(r'(?:[0-9a-fA-F]:?){12}')
                                macs = re.findall(p, message)
                                system_logger.info(self.device['id'] + '  ' + '\n'.join(map(str, macs)));
                            else:
                                data_string = data.decode('utf-8').rstrip();
                                logger.info(self.device['id'] + '  ' + data_string);
                                await server.distribute(self.device['id'], data_string)

                        self.is_error = False
                        time.sleep(0.1)
                    except UnicodeDecodeError as e:  # Bad Baud rate ??
                        await server.distribute(self.device['id'],
                                                "Could not decode serial log. Check Baud rate setting. Currently set to " + properties.baud + "  " + repr(
                                                    e))
                        system_logger.error(
                            "Could not decode serial log. Check Baud rate setting. Currently set to " + properties.baud + "  " + repr(
                                e))
                        error_logger.error(
                            "Could not decode serial log. Check Baud rate setting. Currently set to " + properties.baud + "  " + repr(
                                e))
                        self.is_error = True
            except ConnectionClosed as e:  # try reconnecting
                # ConnectionClosed https://websockets.readthedocs.io/en/stable/faq.html
                pass
            except Exception as e:  # try reconnecting
                system_logger.error("error "+repr(e))
                error_logger.error("error "+repr(e))
                self.is_error = True
               # await server.distribute(self.device['id'], repr(e))
                time.sleep(5)  # retry connection forever

    # Get overriding serial properties if any
    def get_properties(self):
        with self.lock:
            type_properties: SerialProperties = SCATLegacyDevicesMap.devices[self.device['type']];
            if not type_properties:
                type_properties = SerialProperties()

            properties = SerialProperties()

            if 'baud' in self.device['connectionProperties'] and self.device['connectionProperties']['baud']:
                properties.baud = self.device['connectionProperties']['baud']
            else:
                properties.baud = type_properties.baud

            if 'parity' in self.device['connectionProperties'] and self.device['connectionProperties']['parity']:
                properties.parity = self.device['connectionProperties']['parity']
            else:
                properties.parity = type_properties.parity

            if 'stop_bits' in self.device['connectionProperties'] and self.device['connectionProperties']['stop_bits']:
                properties.stop_bits = self.device['connectionProperties']['stop_bits']
            else:
                properties.stop_bits = type_properties.stop_bits

            if 'data_bits' in self.device['connectionProperties'] and self.device['connectionProperties']['data_bits']:
                properties.data_bits = self.device['connectionProperties']['data_bits']
            else:
                properties.data_bits = type_properties.data_bits

            return properties

    # Write messages received from serial port to websocket
    async def send_message(self, message):
        self.ser.write(message.encode())
        if '\n' not in message:
            self.ser.write('\r\n'.encode())

    # Write messages received from serial port to websocket
    async def send_binary_message(self, message):
        self.ser.write(message)

    # Write messages received from serial port to websocket
    async def send_hex_message(self, message):
        self.ser.write(message)

    def send_discover_message(self, callback, message):
        self.discover_mode = True
        self.callback = callback
        self.ser.write(message.encode())
        self.ser.write('\r\n'.encode())
