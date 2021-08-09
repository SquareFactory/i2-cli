"""Copyright (C) Alpine Intuition Sàrl - All Rights Reserved.

This source code is protected under international copyright law. All rights
reserved and protected by the copyright holders.
This file is confidential and only available to authorized individuals with the
permission of the copyright holders. If you encounter this file and do not have
permission, please contact the copyright holders and delete this file.
"""
import docker
import pytest

from i2_client.worker_tester import BuildTestManager

mirror = "examples/tasks/mirror.py"
client = docker.from_env()


def test_init():
    """Test initialization."""
    BuildTestManager()
    BuildTestManager(verbose=True)


def test_build_task():
    """Test worker verification.
    - Test build of docker img
    - Test when docker client not reachable
    - Test wrong Dockerfile

    """

    BuildTestManager().build_task(mirror)
    imgs = client.images.list()
    archipel_imgs = []
    for img in imgs:
        if len(img.tags) == 0:
            continue
        for tag in img.tags:
            if "archipel" in tag or "redis" in tag:
                archipel_imgs.append(tag)
    assert "alpineintuion/archipel-task-mirror:latest" in archipel_imgs

    with pytest.raises(FileNotFoundError):
        BuildTestManager().build_task("zbl")

    with pytest.raises(FileNotFoundError):
        BuildTestManager().build_task(mirror, "zbl", "zbl")


def test_verify_worker(mocker):
    """Test the testing of a worker.
    - Test with working worker
    -
    """

    assert BuildTestManager().verify_worker(mirror)
    mocker.patch(
        "i2_client.worker_tester.BuildTestManager.get_task_class_name",
        return_value="zbl",
    )
    assert not BuildTestManager().verify_worker("examples/simple.py")
