#!/usr/bin/sh

apt update -y

apt install -y \
  libsystemd-dev \
  wkhtmltopdf \
  librsvg2-bin \
  wget \
  libgdal32
