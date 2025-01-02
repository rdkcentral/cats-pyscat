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



class SerialAutoDiscover:

    def discover(self, slot_device_map):
        for key in slot_device_map:
            device = slot_device_map[key]
            device.send_discover_message(self, 'cat /sys/class/net/*/address')

    def discover_off(self, slot_device_map):
        for key in slot_device_map:
            device = slot_device_map[key]
            device.discover_mode = False