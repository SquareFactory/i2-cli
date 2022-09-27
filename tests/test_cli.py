"""Copyright (C) Square Factory SA - All Rights Reserved.

This source code is protected under international copyright law. All rights
reserved and protected by the copyright holders.
This file is confidential and only available to authorized individuals with the
permission of the copyright holders. If you encounter this file and do not have
permission, please contact the copyright holders and delete this file.
"""

from click.testing import CliRunner

from i2_client import i2_cli

runner = CliRunner()
ctx = {"VERBOSE": False}

mirror = "examples/tasks/mirror.py"
mirror_img = "i2-task-mirror:latest"
test_image = "examples/test.jpg"

face_alignment = "examples/tasks/face_alignment/face_alignment.py"
dockerfile = "examples/tasks/face_alignment/Dockerfile"


def test_cli(mocker):
    """Test cli."""
    runner = CliRunner()

    # inference

    mocker.patch("i2_client.client.I2Client.inference")
    mocker.patch("i2_client.cli.client.save_file")

    conn = ["--url", "url", "--access-key", "ak"]

    cmds = [
        ["infer", test_image, *conn],
        ["infer", test_image, *conn, "--save-path", "test.jpg"],
    ]

    # build & verification

    mocker.patch("i2_client.build.BuildManager.build_task")

    cmds += [
        ["build", mirror],
        ["build", face_alignment, "-df", dockerfile],
        ["build", face_alignment, "--dockerfile", dockerfile],
        ["build", mirror, "-nc"],
        ["build", mirror, "--no-cache"],
        ["build", mirror, "--cpu"],
        ["build", mirror, "-ba", "TEST"],
        ["build", mirror, "--build-args", "TEST"],
        ["build", mirror, "--build-args", "TEST", "--build-args", "TEST"],
        ["test", mirror_img],
    ]

    for cmd in cmds:
        print("i2 " + " ".join(cmd))
        results = runner.invoke(i2_cli, cmd, obj=ctx)
        assert results.exit_code == 0, vars(results)
