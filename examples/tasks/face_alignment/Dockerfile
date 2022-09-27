# Copyright (C) Square Factory SA - All Rights Reserved.
#
# This source code is protected under international copyright law. All rights
# reserved and protected by the copyright holders.
# This file is confidential and only available to authorized individuals with the
# permission of the copyright holders. If you encounter this file and do not have
# permission, please contact the copyright holders and delete this file.

FROM alpineintuition/archipel-base-cpu:latest

RUN apt-get update --fix-missing && \
    apt-get install -y \
      python3-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN pip install \
      Cython==0.29.21 \
      onnxruntime==1.6.0 \
      scipy==1.6.1 \
      torch==1.7.1 \
      torchvision==0.8.2

RUN git clone https://github.com/cleardusk/3DDFA_V2 /opt/3ddfa && \
    cd /opt/3ddfa && ./build.sh