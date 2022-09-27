"""Copyright (C) Square Factory SA - All Rights Reserved.

This source code is protected under international copyright law. All rights
reserved and protected by the copyright holders.
This file is confidential and only available to authorized individuals with the
permission of the copyright holders. If you encounter this file and do not have
permission, please contact the copyright holders and delete this file.
"""

import re

from setuptools import find_packages, setup

with open("i2_client/__init__.py") as f:
    version = re.search(r"\d.\d.\d", f.read()).group(0)  # type: ignore


setup(
    name="i2_client",
    version=version,
    install_requires=[
        "archipel-utils==0.1.7",
        "click>=8.0",
        "docker>=4.4",
        "imutils>=0.5.4",
        "msgpack>=1.0",
        "numpy>=1.19",
        "rich>=10.13",
        "websockets>=8.1",
        "opencv-python==4.6.0.66",
    ],
    packages=find_packages(),
    entry_points="""
        [console_scripts]
        i2py=i2_client:i2_cli
    """,
    python_requires=">=3.7",
)
