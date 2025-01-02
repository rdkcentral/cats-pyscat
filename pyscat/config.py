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



import configparser
import logging
import os


class SCATDevicesConfig:
    config_file_path = None
    trace_regex: str = None
    trace_log_base: str = "logs/"

    def __init__(self, prop):
        self.config_file_path = prop.get('devices_config_file_path')
        self.trace_regex = prop.get('trace_regex')
        self.trace_log_base = prop.get('trace_log_base')

class DIGICredentials:
    digi_username: str = None
    digi_password: str = None
    def __init__(self, prop):
        self.digi_username = prop.get('digi_username')
        self.digi_password = prop.get('digi_password')


class Config:
    env: str = None
    devices_config: SCATDevicesConfig = None

    def __init__(self):
        config_file = "pyscat/config/config.ini"
        parser = configparser.ConfigParser()
        parser.read(config_file)
        self.devices_config = SCATDevicesConfig(parser[os.environ['ENVIRONMENT']])

class DIGIConfig:
    digi_credentials: DIGICredentials = None

    def __init__(self):
        config_file = "pyscat/config/config.ini"
        parser = configparser.ConfigParser()
        parser.read(config_file)
        self.digi_credentials = DIGICredentials(parser["digi"])