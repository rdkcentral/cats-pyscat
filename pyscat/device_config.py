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



import json
from pyscat.config import SCATDevicesConfig
from pyscat.devices import Devices
import re
from itertools import filterfalse
import logging
# Read devices.json file
from pyscat.slot_mapping import SlotMapping


class DeviceConfig:
    scat_devices: Devices

    def __init__(self, devices_config: SCATDevicesConfig):
        self.devices_config = devices_config
        self.system_logger = logging.getLogger('system')

    def read_device_config(self):
        f = open(self.devices_config.config_file_path)
        devices_config_str: str = f.read()
        self.scat_devices = json.loads(devices_config_str)
        self.print_mapping()
        return self.scat_devices

    def write_device_config(self, slot_mapping):
        scat_config = json.dumps(slot_mapping,indent=4)
        f = open(self.devices_config.config_file_path, 'w')
        f.write(scat_config)
        return

    def print_mapping(self):
        if self.scat_devices is not None:
            for device in self.scat_devices['devices']:
                slot = int(device['id'][-3:], 16)
                component = int(device['id'][-5:-4])
                port = device['connectionProperties']['port']
                x = re.search(self.devices_config.trace_regex, port)


    def get_config(self):
        return self.scat_devices

    def check_mapping_contains_zero(self, stringDeviceID, stringOutlet):
        #combine the deviceID and Outlet to check if they contain 0
        stringVal = stringDeviceID+stringOutlet
        # Regular expression to match a single '0' but not '10', '20', etc.
        pattern = r'^(?!.*\b0\b).*'
        return bool(re.match(pattern, stringVal))

    def delete_slot_mapping(self, slot):
        if self.scat_devices['devices']:
            slot_hex = f"{int(slot):03x}".upper()
            for device in self.scat_devices['devices'][:]:
                if device['id'].endswith(slot_hex):
                    self.scat_devices['devices'].remove(device)

            self.write_device_config(self.scat_devices)

    def update_slot_mapping_for_slot(self, slot, value):
        if self.scat_devices['devices'] is not None:
            self.delete_slot_mapping(slot)

            if value:
                if isinstance(value, list):
                    for idx, mapping in enumerate(value):
                        mapped_device = self.parse_mapping(slot, mapping, idx)
                        self.scat_devices['devices'].append(mapped_device)
                else:
                    mapped_device = self.parse_mapping(slot, value, 0)
                    self.scat_devices['devices'].append(mapped_device)

            self.write_device_config(self.scat_devices)

    def update_slot_mapping(self, slot_mapping: SlotMapping):
        try:
            if slot_mapping is None:  # 1:1 mapping is not supported as we dont know the number of devices in the rack.
                raise Exception(
                    "Default slot mapping is not available in SCAT. There is no config that identifies device "
                    "config.")
            elif 'slots' in slot_mapping and slot_mapping['slots'] is not None:
                devices = {'devices': []}
                for slot in slot_mapping['slots']:
                    value = slot_mapping['slots'][slot]
                    if value:
                        if isinstance(value, list):
                            for idx, mapping in enumerate(value):
                                device = self.parse_mapping(slot, mapping, idx)
                                devices['devices'].append(device)
                        else:
                            device = self.parse_mapping(slot, value, 0)
                            devices['devices'].append(device)

                self.write_device_config(devices)
                self.read_device_config()  # update the config
            elif 'devices' in slot_mapping and slot_mapping['devices'] is not None:  # slot mapping in devices.json format
                self.write_device_config(slot_mapping)
                self.read_device_config()  # update the config
            else:
                raise ValueError("Invalid slot mapping")
        except KeyError as e:
            raise ValueError("Invalid slot mapping format") from e
        except TypeError as e:
            raise ValueError("Invalid slot mapping format") from e

    def parse_mapping(self, slot, value, idx):
        if value == 'N/A':
            raise ValueError("N/A mapping is not supported for SCAT. You can leave out the slot in the slot mapping instead.")
        self.system_logger.info("Slot "+str(slot) + " mapping " + str(value))

        try:
            is_updatedBaudRate = False
            outlet_info = value.split(':')
            device_id = outlet_info[0]
            outlet = outlet_info[1]
            if len(outlet_info) == 3:
                baudRate = outlet_info[2]
                is_updatedBaudRate= True
            
            if not (self.check_mapping_contains_zero(device_id, outlet)):
                raise ValueError("0 mapping is not supported for SCAT. Digi Mapping start with 1 for example 1:1")
                print("*defaultBaudRate=",is_defaultBaudRate)
            else:
                self.system_logger.info("In Parse Mapping :: Slot "+str(slot) + " mapping " + str(value))
            
        except IndexError as e:
            raise ValueError("Invalid mapping: Slot "+str(slot) + " mapping " + str(value)) from e
        
        if is_updatedBaudRate:
            if not baudRate.strip():
                raise ValueError("Invalid mapping: Baud can't be empty or NULL String")
            else:
                device = self.get_device_config_with_baud(slot, device_id, outlet, baudRate, idx)
        else:
            device = self.get_device_config(slot, device_id, outlet,idx)
        return device

    def get_device_config_with_baud(self, slot, device_id, outlet, baudRate, idx):
        id: str = ''
        if idx == 0:
            id = f"{int(slot):012x}".upper()
        else:
            id = '0000000' + str(idx) + f"{int(slot):04x}".upper()

        zero_based_outlet = int(outlet) - 1
        zero_based_device_id = int(device_id) - 1
        tty_outlet = f"{int(zero_based_outlet):02}".upper()
        tty = "/dev/ttyO" + str(zero_based_device_id) + "" + tty_outlet

        device = {'id': id, 'type': "DTA", 'connectionProperties': {'port': tty, 'baud':int(baudRate)}}
        return device

    def get_device_config(self, slot, device_id, outlet, idx):
        id: str = ''
        if idx == 0:
            id = f"{int(slot):012x}".upper()
        else:
            id = '0000000' + str(idx) + f"{int(slot):04x}".upper()

        zero_based_outlet = int(outlet) - 1
        zero_based_device_id = int(device_id) - 1
        tty_outlet = f"{int(zero_based_outlet):02}".upper()
        tty = "/dev/ttyO" + str(zero_based_device_id) + "" + tty_outlet

        device = {'id': id, 'type': "DTA", 'connectionProperties': {'port': tty}}
        return device

