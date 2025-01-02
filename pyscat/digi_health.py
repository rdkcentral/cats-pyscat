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



import requests
import telnetlib
from pyscat.config import DIGIConfig
import logging
from os import environ
import re
import asyncio
import time

class DigiHealth:
    __digi_username = None
    __digi_password = None
    __is_digi_on_rack = False
    __digi_device_ips=[]

    def __init__(self):
        self.system_logger = logging.getLogger('system')

    @staticmethod
    def get_digi_username():
        if DigiHealth.__digi_username == None:
            DigiHealth.set_digi_credentials()
        return DigiHealth.__digi_username
    
    @staticmethod
    def get_digi_password():
        if DigiHealth.__digi_password == None:
            DigiHealth.set_digi_credentials()
        return DigiHealth.__digi_password
    
    @staticmethod
    def set_digi_credentials():
        digi_username = environ.get("digi_username")
        digi_password = environ.get("digi_password")
        if digi_username == None or digi_password is None:
            digi_config = DIGIConfig()
            digi_username = digi_config.digi_credentials.digi_username
            digi_password = digi_config.digi_credentials.digi_password
        DigiHealth.__digi_username = digi_username
        DigiHealth.__digi_password = digi_password

    def get_is_digi_on_rack(self):
        return self.__is_digi_on_rack

    def login_to_digi(self, host):
        tn = telnetlib.Telnet(host, 23)
        time.sleep(1)
        tn.read_until(b"login: ")
        tn.write(DigiHealth.get_digi_username().encode('ascii')+b"\n")
        time.sleep(1)
        response = tn.read_very_eager()
        if 'password:' or'Password:' in response.decode('utf-8').split("\n"):
            tn.write(DigiHealth.get_digi_password().encode('ascii')+b"\n")
            time.sleep(3)
        return tn
    
    async def reboot_digi(self,host):
        logging.info("reboot_digi")
        is_rebooting = False
        try:
            tn = self.login_to_digi(host)
            time.sleep(1)
            tn.write("boot action=reset".encode('ascii')+b"\n")
            time.sleep(4)
            response = tn.read_very_eager()
            logging.info(response)
            for line in response.decode('utf-8').split("\n"):
                if "rebooting..." or "The system is going down for reboot NOW!" in line:
                    is_rebooting = True
            tn.close()
            logging.info("Is Digi with ip {} rebooting? {}".format(host,str(is_rebooting)))		
            return is_rebooting
        except Exception as e:
            logging.info(e)	
            return is_rebooting
        
    async def set_real_port_profiles(self,host):
        logging.info("set_real_port_profiles")
        try:
            tn = self.login_to_digi(host)
            time.sleep(1)
            tn.write("set profile profile=realport port=1-32".encode('ascii')+b"\n")
            time.sleep(5)
            tn.write("show profile".encode('ascii')+b"\n")
            time.sleep(3)
            response = tn.read_very_eager()
            if 'error' in response:
                tn.write("set profile profile=realport range=1-4".encode('ascii')+b"\n")
                time.sleep(5)
                response = tn.read_very_eager()
            logging.info(response)
            tn.close()	
        except Exception as e:
            logging.info(e)	

    def check_digi_status(self, host):
        logging.info("checking digi status")
        try:
            tn = self.login_to_digi(host)
            time.sleep(1)
            if tn.sock is not None and tn.sock.fileno() != -1:
                digi_status = True
            tn.close()
            return digi_status
        except Exception as e:
            logging.info(e)
            return False
        
    def get_digi_uptime(self,host):
        logging.info("checking Digi uptime")
        try:
            tn = self.login_to_digi(host)
            time.sleep(1)
            tn.write("uptime".encode('ascii')+b"\n")
            time.sleep(2)
            response = tn.read_very_eager()
            logging.info(response)
            if "Error" in response.decode('utf-8'):
                tn.write("display device".encode('ascii')+b"\n")
                time.sleep(3)
                response = tn.read_very_eager()
                logging.info(response)
            if "Time" in response.decode('utf-8'):
                uptime = response.decode('utf-8').split("\n")[3].split("reboot:")[1].strip()
            elif "uptime" in response.decode('utf-8'):
                uptime = response.decode('utf-8').split("\n")[10].split(": ")[1].strip()
            tn.close()
            return {"uptime" : uptime}
        except Exception as e:
            return {"uptime" : "unable to fetch"}
        
    def get_digi_version(self,host):
        logging.info("checking Digi version")
        try:
            tn = self.login_to_digi(host)
            time.sleep(1)
            tn.write("show versions".encode('ascii')+b"\n")
            time.sleep(1)
            response = tn.read_very_eager()
            logging.info(response)
            if "Error" in response.decode('utf-8'):
                tn.write("display device".encode('ascii')+b"\n")
                time.sleep(3)
                response = tn.read_very_eager()
                logging.info(response)
            if "Factory" in response.decode('utf-8'):
                version = response.decode('utf-8').split("\n")[9].split("release_")[1].strip()
            elif "firmware" in response.decode('utf-8'):
                version = response.decode('utf-8').split("\n")[7].split(": ")[1].strip()
            tn.close()
            return {"Firmware" : version}
        except Exception as e:
            return {"Firmware" : "Unable to fetch"}
    
    def get_digi_mac(self,host):
        logging.info("Fetching digi mac")
        try:
            tn = self.login_to_digi(host)
            time.sleep(1)
            tn.write("show config".encode('ascii')+b"\n")
            time.sleep(1)
            response = tn.read_very_eager()
            logging.info(response)
            if "Error" in response.decode('utf-8'):
                tn.write("display device".encode('ascii')+b"\n")
                time.sleep(3)
                response = tn.read_very_eager()
                logging.info(response)
            mac_regex = r"([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})"
            mac_match = re.search(mac_regex, response.decode('utf-8'))
            mac= mac_match.group(0)
            tn.close()
            return {"mac" : mac}
        except Exception as e:
            return {"mac" : "Unable to fetch"}


    def get_digi_devices(self):
        digi_device_ips = []
        try:
            response = requests.get("http://192.168.100.11/mtquery/api/v2/router/capability")
            data = response.json()
            if "TCE" in data and "metadata" in data["TCE"]:
                self.__is_digi_on_rack = True
                for digi_device in data["TCE"]["metadata"]:
                    digi_device_ips.append(digi_device["address"])
            self.__digi_device_ips = digi_device_ips
            logging.info(self.__digi_device_ips)
            return self.__digi_device_ips
        except requests.exceptions.RequestException as e:
            print(f"HTTP Request failed: {e}")
        except ValueError:
            print("Invalid JSON response")

    async def reboot_digi_devices(self):
        digi_device_ips = self.__digi_device_ips
        tasks = [self.reboot_digi(digi_ip) for digi_ip in digi_device_ips]
        return await asyncio.gather(*tasks)
    
    async def set_real_port_to_digi(self):
        digi_device_ips = self.__digi_device_ips
        tasks = [self.set_real_port_profiles(digi_ip) for digi_ip in digi_device_ips]
        return await asyncio.gather(*tasks) 