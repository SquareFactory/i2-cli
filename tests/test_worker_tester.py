"""Copyright (C) Alpine Intuition Sàrl - All Rights Reserved.

This source code is protected under international copyright law. All rights
reserved and protected by the copyright holders.
This file is confidential and only available to authorized individuals with the
permission of the copyright holders. If you encounter this file and do not have
permission, please contact the copyright holders and delete this file.
"""

import os
from pathlib import Path

import docker
import pytest

from i2_client.worker_tester import BuildTestManager

mirror = Path("examples/tasks/mirror.py")
client = docker.from_env()


def test_init():
    """Test initialization."""
    BuildTestManager()
    BuildTestManager(verbose=True)


class cd:
    """Context manager for changing the current working directory."""

    def __init__(self, new_path):
        self.new_path = Path(new_path).resolve()

    def __enter__(self):
        """Save current working dir and change to new one."""
        self.saved_path = Path.cwd()
        os.chdir(self.new_path)

    def __exit__(self, etype, value, traceback):
        """Change current dir to saved one."""
        os.chdir(self.saved_path)


def test_build_task(mocker):
    """Test worker verification.

    - Test build of docker img
    - Test when docker client not reachable
    - Test wrong Dockerfile

    """

    with cd(mirror.parent):
        BuildTestManager().build_task(mirror.name, cpu=True)

        archipel_imgs = []
        for img in client.images.list():
            if len(img.tags) == 0:
                continue
            for tag in img.tags:
                if "archipel" in tag or "redis" in tag:
                    archipel_imgs.append(tag)
        assert "alpineintuion/archipel-task-mirror:latest" in archipel_imgs

        print("script do not exist")
        with pytest.raises(FileNotFoundError):
            BuildTestManager().build_task("zbl")

        print("dockerfile do not exist")
        with pytest.raises(FileNotFoundError):
            BuildTestManager().build_task(mirror.name, "zbl", "zbl")

        print("dockerfile is not in the build context")
        #  mocker.patch("pathlib.Path.is_file", return_value=False)
        with pytest.raises(ValueError):
            BuildTestManager().build_task(mirror.name, dockerfile="../zbl")


def test_verify_worker(mocker):
    """Test full pipeline of worker testing."""
    with cd(mirror.parent):
        assert BuildTestManager(verbose=True).verify_worker(mirror.name)
