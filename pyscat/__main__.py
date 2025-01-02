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

from starlette.requests import Request
from fastapi import FastAPI
import uvicorn
from starlette.responses import Response

from pyscat.config import Config
from pyscat.device_config import DeviceConfig
from pyscat.devices import Devices
from pyscat.log_config import LogConfig
from pyscat.serial.serial_connection_manager import SerialConnectionManager
from pyscat.serial.serial_health import SerialHealthCheck
from pyscat.websocket_server import WebSocketServer
import websockets
import asyncio
import threading
import codecs
from  pyscat.digi_health import DigiHealth


def process_request(path, header):
    slot = path.strip("/")
    found = False
    print(devices)
    for device in devices['devices']:
        if device['id'] == slot:
            found = True
            break

    if not found:
        raise ConnectionRefusedError


def loop_in_thread(loop):
    asyncio.set_event_loop(loop)
    loop.run_until_complete(start_server)
    loop.run_forever()

def initialize_device_config():
    config = Config() 
    return DeviceConfig(config.devices_config)

app = FastAPI()
serial_health = SerialHealthCheck()
device_config = initialize_device_config()
devices = device_config.read_device_config()
device_type = devices.get('deviceType', None)
if device_type != 'UART': 
        digi = DigiHealth()
        digi.get_digi_devices()

# Support Rest API from Swagger
@app.get('/scat/api/devices/')
def devices():
    return device_config.get_config()


@app.post('/scat/api/device/{deviceid}/write')
async def device_write(deviceid, request: Request):
    message_bytes = await request.body()

    if message_bytes is not None and request.headers['Content-Type'] == 'application/octet-stream':
        await server.send_binary_to_serial(deviceid, message_bytes)
    else:

        # this is hex string (backward compatibility)
        hex_string = codecs.decode(message_bytes, 'hex')

        await server.send_hex_to_serial(deviceid, hex_string)

    return {"success": True}


@app.post('/scat/api/slotMapping')
async def update_slot_mapping(request: Request):
    slot_mapping = await request.json()
    device_config.update_slot_mapping(slot_mapping)
    serial_connection_manager.update_devices(device_config.read_device_config())
    return {"success": True}


@app.put('/scat/api/slotMapping/{slot}')
async def update_slot_mapping_for_slot(slot, request: Request):
    slot_mapping = await request.json()
    device_config.update_slot_mapping_for_slot(slot, slot_mapping)
    serial_connection_manager.update_devices(device_config.read_device_config())
    return {"success": True}


@app.delete('/scat/api/slotMapping/{slot}')
async def delete_slot_mapping_for_slot(slot):
    device_config.delete_slot_mapping(slot)
    serial_connection_manager.update_devices(device_config.read_device_config())
    return {"success": True}


@app.get("/")
async def root():
    return {"message": "SCAT is up"}


@app.get("/scat")
async def get_scat_config():
    return device_config.get_config()


@app.get('/scat/api/health')
def health():
    return serial_health.get_health()

@app.post('/scat/reboot')
async def reboot():
    await reboot_trace_devices()

@app.post('/scat/profile')
async def set_profile():
    await set_real_port_to_digi_devices()

async def reboot_trace_devices():
    await digi.reboot_digi_devices() #logic can be extended to other trace devices if exists in future

async def set_real_port_to_digi_devices():
    await digi.set_real_port_to_digi()

@app.exception_handler(ValueError)
async def validation_exception_handler(request, exc: Exception):
    print(str(exc))
    return Response("Illegal Argument : " + str(exc), status_code=400)

if __name__ == "__main__":
    # app.run(debug=True)
    print("SCAT starting")
    config = Config()
    system_logger = LogConfig.setup_logger('system', config.devices_config.trace_log_base + "/"
                                                                                            'system' + ".log")
    system_logger.info("SCAT starting")
    device_config = DeviceConfig(config.devices_config)
    devices = device_config.read_device_config()
    # Start Websocket Server
    server = WebSocketServer()
    start_server = websockets.serve(server.ws_handler, '0.0.0.0', 15080, process_request=process_request)
    # Start Serial Connection to Serial ports
    serial_connection_manager = SerialConnectionManager(devices, server)
    serial_connection_manager.connect_to_devices()
    loop = asyncio.get_event_loop()
    t = threading.Thread(target=loop_in_thread, args=(loop,))
    t.start()
    uvicorn.run(app, host="0.0.0.0", port=9080, log_level="info")
