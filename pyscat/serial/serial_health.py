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



import logging

from pyscat.config import Config
from pyscat.devices import Devices
from pyscat.health import HealthStatus, HealthReport
from pyscat.serial.serial_properties import SerialProperties
from pkg_resources import get_distribution, DistributionNotFound
from pyscat.device_config import DeviceConfig
from serial import Serial, SerialException
from pyscat.digi_health import DigiHealth


def get_version():
    try:
        return get_distribution('pyscat').version
    except DistributionNotFound:
        return "Could not identify version"


class SerialHealthCheck:

    def __init__(self):
        config = Config()
        self.system_logger = logging.getLogger('system')
        device_config = DeviceConfig(config.devices_config)
        self.deviceList: Devices = device_config.read_device_config()
        

    def report_health(self, slot_device_map):
        for key in slot_device_map:
            device = slot_device_map[key]
            self.system_logger.info(key + '  Connected :' + str(not device.is_error))

    def get_health(self):
        health_status = HealthStatus()
        health_status.version = {'MS_VERSION': get_version()}
        health_status.hw_devices_health_status = self.get_hw_health()
        health_status.dependencies_health_status = self.get_serial_port_health()
        if health_status.dependencies_health_status is None:
            health_status.is_healthy = False
            return health_status

        for report in health_status.dependencies_health_status:
            if not report.is_healthy:
                health_status.is_healthy = False
                health_status.remarks = "Serial ports is unhealthy"
                return health_status

        health_status.is_healthy = True
        return health_status

    def get_serial_port_health(self):
        hw_statuses = []
        for device in self.deviceList['devices']:
            serial_port = device['connectionProperties']['port']
            hw_status: HealthReport = HealthReport()
            hw_status.entity = serial_port
            hw_status.device_id = device['id']
            if 'baud' in device['connectionProperties'] and device['connectionProperties']['baud']:
                baud = device['connectionProperties']['baud']
            else:
                baud = SerialProperties.baud;

            try:
                ser = Serial(serial_port, baud, timeout=1)
                hw_status.is_healthy = ser.isOpen()
            except SerialException as e:
                hw_status.is_healthy = False
                hw_status.remarks = str(e)

            hw_statuses.append(hw_status)
        return hw_statuses
    
    def get_hw_health(self):
        device_type = self.deviceList.get('deviceType', None)
        if device_type != 'UART':
            digi_health = DigiHealth()
            digi_ips = digi_health.get_digi_devices()
            if digi_health.get_is_digi_on_rack():
                return self.get_digi_health(digi_health,digi_ips)
  
    def get_digi_health(self,digi_health,digi_ips):
        hw_statuses=[]
        count =0
        for digi_ip in digi_ips:
            count=count+1
            hw_status: HealthReport = HealthReport()
            hw_status.entity = "Digi Connect"
            hw_status.device_id = str(count)
            hw_status.host = digi_ip
            hw_status.is_healthy = digi_health.check_digi_status(digi_ip)
            hw_status.is_healthy = True
            if hw_status.is_healthy:
                hw_status.version = digi_health.get_digi_version(digi_ip)
                uptime = digi_health.get_digi_uptime(digi_ip)
                mac = digi_health.get_digi_mac(digi_ip)
                hw_status.metadata = dict(list(uptime.items()) + list(mac.items()))
            hw_statuses.append(hw_status)
        return hw_statuses