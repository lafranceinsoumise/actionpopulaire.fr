FROM ubuntu:20.04

ENV TZ=Etc/UTC
ENV PYTHON_KEYRING_BACKEND="keyring.backends.null.Keyring"

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN apt-get update
RUN apt-get upgrade -y

RUN apt-get install python3.9 python3.9-dev python3.9-venv python3.9-distutils -y
RUN apt-get install python3-pip build-essential git language-pack-fr libgdal-dev jq libsystemd-dev -y
RUN apt-get install librsvg2-bin
RUN ln -sfn /usr/bin/python3.9 /usr/bin/python3
RUN pip3 install poetry
