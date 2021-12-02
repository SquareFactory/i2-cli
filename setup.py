"""Copyright (C) Alpine Intuition Sàrl - All Rights Reserved.

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
        "archipel-utils>=0.1.6",
        "click>=8.0",
        "docker>=4.4",
        "enlighten>=1.10",
        "msgpack>=1.0",
        "numpy>=1.19",
        "opencv-python>=4.5",
        "rich>=10.13",
        "websockets>=8.1",
    ],
    packages=find_packages(),
    entry_points="""
        [console_scripts]
        i2=i2_client:i2_cli
    """,
    python_requires=">=3.8",
)
