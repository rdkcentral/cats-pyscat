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



from typing import List

from pyscat.devices import Devices
from serial import Serial
from pyscat.serial.device_serial import DeviceSerialConnection


# Serial connection Manager
class SerialConnectionManager:
    ser: Serial = None
    device_serial_connections: List[DeviceSerialConnection]

    def __init__(self, devices: Devices, server):
        self.devices = devices
        self.device_serial_connections = []
        self.server = server

    def update_devices(self, devices: Devices):
        for device_serial_connection in self.device_serial_connections:
            device_serial_connection.close_connection_to_device()

        self.device_serial_connections = []
        self.devices = devices
        self.connect_to_devices()

    def connect_to_devices(self):
        for device in self.devices['devices']:
            device_serial_connection: DeviceSerialConnection = DeviceSerialConnection(device)
            device_serial_connection.connect_to_device(self.server)
            self.device_serial_connections.append(device_serial_connection)