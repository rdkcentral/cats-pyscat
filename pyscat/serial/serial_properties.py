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



import serial

# Default Serial Properties
class SerialProperties:
    baud: int = 115200
    parity = serial.PARITY_NONE
    data_bits = serial.EIGHTBITS
    stop_bits = serial.STOPBITS_ONE

    def __init__(self, baud=115200, parity=serial.PARITY_NONE, data_bits=8, stop_bits=1):
        self.baud = baud
        self.parity = parity
        self.data_bits = data_bits
        self.stop_bits = stop_bits


class SCATLegacyDevicesMap:
    DTA = SerialProperties()

    devices = {
        "DTA": DTA
    }
