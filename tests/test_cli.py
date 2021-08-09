"""Copyright (C) Alpine Intuition Sàrl - All Rights Reserved.

This source code is protected under international copyright law. All rights
reserved and protected by the copyright holders.
This file is confidential and only available to authorized individuals with the
permission of the copyright holders. If you encounter this file and do not have
permission, please contact the copyright holders and delete this file.
"""

import cv2
from click.testing import CliRunner

from i2_client import cli

ctx = {"VERBOSE": False}
test_image = cv2.imread("examples/test.jpg")


def test_cli(mocker):
    """Test cli."""
    runner = CliRunner()
    cmds = ["infer", "test"]
    for cmd in cmds:
        cmd += " --help"
        print(f"i2 {cmd}")
        assert runner.invoke(cli, cmd.split(), obj=ctx).exit_code == 0
