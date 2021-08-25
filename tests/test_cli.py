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

runner = CliRunner()
ctx = {"VERBOSE": False}
mirror = "examples/tasks/mirror.py"
test_image = cv2.imread("examples/test.jpg")


def test_cli(mocker):
    """Test cli."""
    runner = CliRunner()
    cmds = ["infer", "test"]
    for cmd in cmds:
        cmd += " --help"
        print(f"i2 {cmd}")
        assert runner.invoke(cli, cmd.split(), obj=ctx).exit_code == 0


def test_cli_test_worker(mocker):
    """Test test worker cli."""

    mocker.patch("i2_client.worker_tester.BuildTestManager.verify_worker")

    cmds = [
        ["test", "worker", mirror, "--build-args", "TEST"],
        ["test", "worker", mirror, "--build-args", "TEST", "--build-args", "TEST"],
    ]
    for cmd in cmds:
        results = runner.invoke(cli, cmd, obj=ctx)
        assert results.exit_code == 0, results
