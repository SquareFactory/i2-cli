"""Copyright (C) Alpine Intuition Sàrl - All Rights Reserved.

This source code is protected under international copyright law. All rights
reserved and protected by the copyright holders.
This file is confidential and only available to authorized individuals with the
permission of the copyright holders. If you encounter this file and do not have
permission, please contact the copyright holders and delete this file.
"""

from setuptools import find_packages, setup

setup(
    name="archipel_client",
    version="0.0.1",
    install_requires=[
        "archipel-utils",
        "msgpack==1.0.0",
        "numpy==1.19.4",
        "opencv-python==4.5.1.48",
        "websockets==8.1",
    ],
    packages=find_packages(),
    python_requires=">=3.8",
)
