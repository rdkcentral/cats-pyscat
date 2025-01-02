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



from datetime import datetime
from typing import List

from fastapi_camelcase import CamelModel


class LeaseMetadata(CamelModel):
    address: str = None
    comment: str = None
    disabled: bool = None
    is_healthy: bool = None
    mac_address: str = None
    status: str = None


class RouterLeaseStatus(CamelModel):
    metadata: List[LeaseMetadata] = []
    is_healthy: bool = None
    comment: str = None


class HealthReport(CamelModel):
    entity: str = None
    device_id: str = None
    is_healthy: bool = None
    remarks: str = None
    host : str = None
    version: dict = None
    metadata: dict = None


class License(CamelModel):
    name: str = None
    remarks: str = None
    expiry_date: datetime = None
    max_property_count: str = None
    metadata: dict = None


class HealthStatus(CamelModel):
    version: dict = None
    is_healthy: bool = None
    remarks: str = None
    lease_health_status: RouterLeaseStatus = None
    hw_devices_health_status:List[HealthReport] = []
    dependencies_health_status: List[HealthReport] = []
    licenses: List[License] = []
    metadata: dict = None





