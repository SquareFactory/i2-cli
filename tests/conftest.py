"""Copyright (C) Square Factory SA - All Rights Reserved.

This source code is protected under international copyright law. All rights
reserved and protected by the copyright holders.
This file is confidential and only available to authorized individuals with the
permission of the copyright holders. If you encounter this file and do not have
permission, please contact the copyright holders and delete this file.
"""
import shutil

import pytest


@pytest.fixture()
def delete_zbeul_dir():
    """Remove test directory if used."""
    yield
    shutil.rmtree("zbeul")
