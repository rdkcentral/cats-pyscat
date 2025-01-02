FROM --platform=$BUILDPLATFORM python:3.12-alpine
ARG TARGETARCH
ARG BUILDPLATFORM   
ARG TARGETPLATFORM
ARG TARGETOS

COPY . /pyscat
WORKDIR /pyscat

RUN mkdir /var/log/scat
RUN  mkdir /etc/scat

RUN echo "Building on $BUILDPLATFORM, building for $TARGETPLATFORM"

RUN apk update && apk add bash

RUN \
    apk add --no-cache --virtual .build-deps libressl-dev musl-dev libffi-dev gcc libc-dev  && \
    python3 -m pip install -r requirements.txt --trusted-host pypi.python.org --no-cache-dir && \
    apk --purge del .build-deps && python3 -m pip uninstall py

RUN pip install --trusted-host pypi.python.org --no-cache-dir -r requirements.txt

EXPOSE 15080
EXPOSE 9080
EXPOSE 15002
CMD  python3 -m pyscat
