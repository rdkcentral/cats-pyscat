# PYSCAT Microservice

Pyscat microservice supports streaming data from a serial port over IP using WebSocket technology. The hardware emulates virtual serial COM ports, allowing seamless integration with existing applications. This microservice is responsible for streaming the serial data over a WebSocket connection, ensuring efficient and reliable data transmission.


## Development Setup
```
python -m pyscat -e development
or
ENVIRONMENT=development python -m pyscat
```

## Building

Run the below command in root directory as required by the [Dockerfile](Dockerfile) to build application as a Docker container.

* `docker build -t="/pyscat" .`


### Supported Mappings

**IMPORTANT : SCAT DEVICE IDs START USUALLY WITH 0 AND NOT 1**

- Can be represented as a list or string
```
{"slots":{"1":["1:1","1:2"],"2":["1:2"],"3":"1:3","4":"1:4"}}
```

- Supports actual devices.json format
```
{
    "devices": [
        {
            "id": "000000000001",
            "type": "DTA",
            "connectionProperties": {
                "port": "ttyO100"
            }
        },
        {
            "id": "000000010001",
            "type": "DTA",
            "connectionProperties": {
                "port": "ttyO101"
            }
        }
    ]
}
```

## NGINX Configuration
NGINX is used to support a unified path for communication to the rack microservices as well as communication between the rack microservices. NGINX configuration for pyscat can be found at [pyscat.conf](/conf/pyscat.conf). This configuration file is used to route requests to the Pyscat microservice.


## Supported Serial Device Hardware
The supported types are listed below:

| Hardware Type  | Hardware Type Identifiers | Connection Protocol | Documentation                                                                                                                                         |
|----------------|---------------------------|---------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------|
| Digi ConnectPort | Digi ConnectPort TS 16/32 | Serial              | [Digi ConnectPort Docs](https://hub.digi.com/support/products/infrastructure-management/digi-connectport-lts-8-16-32-terminal-server/#specifications) |


## Access the Swagger Documentation
The Swagger Documentation for the Pyscat Microservice can be accessed at http://localhost:9080/docs when running locally. Default swagger path is /docs.



## Health Check
```
GET http://localhost:9090/scat/api/health 
```
