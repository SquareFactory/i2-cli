"""Copyright (C) Alpine Intuition Sàrl - All Rights Reserved.

This source code is protected under international copyright law. All rights
reserved and protected by the copyright holders.
This file is confidential and only available to authorized individuals with the
permission of the copyright holders. If you encounter this file and do not have
permission, please contact the copyright holders and delete this file.
"""

import os
from pathlib import Path
from tempfile import NamedTemporaryFile

import docker
import pytest

from i2_client.worker_tester import BuildTestManager

mirror = Path("examples/tasks/mirror.py")
docker_img = "alpineintuion/archipel-task-mirror:latest"
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
        assert docker_img in archipel_imgs

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


def test_get_worker_classs_name():
    """Test get worker class name.

    Tested:
        - field not present
        - multiple fields
        - sanitize inputs
    """

    bm = BuildTestManager()

    print("No valid field into file")
    with NamedTemporaryFile() as tmp_file:
        tmp_file.write(b"no field")
        tmp_file.seek(0)
        with pytest.raises(AttributeError):
            bm.get_worker_class_name(tmp_file.name)

    print("Multiple definitions")
    with NamedTemporaryFile() as tmp_file:
        tmp_file.write(b"__task_class_name__ = 'zbl'\n")
        tmp_file.write(b"__task_class_name__ = 'zbl'\n")
        tmp_file.seek(0)
        with pytest.raises(AttributeError):
            bm.get_worker_class_name(tmp_file.name)

    print("Sanize inputs")
    with NamedTemporaryFile() as tmp_file:
        tmp_file.write(b"__task_class_name__ = 'zbl_.;l'\n")
        tmp_file.seek(0)
        worker_class = bm.get_worker_class_name(tmp_file.name)
        assert worker_class == "zbl_l"


def test_test_worker(mocker):
    """Test test worker function.

    Tested:
        - docker image not built
        - error during unit testing start
        - unit test successful
        - unit test not successful
    """

    btm = BuildTestManager()

    print("Image do not exist")
    with pytest.raises(RuntimeError):
        btm.test_worker("zbl", "zbl")
        assert False

    print("Error during unit testing")
    func = "docker.models.containers.ContainerCollection.run"

    def raise_error(*args, **kargs):
        raise docker.errors.ContainerError("", "", "", "", "")

    mocker.patch(func, side_effect=raise_error)
    success = btm.test_worker("zbl", "zbl")
    assert not success

    print("Worker test successful")
    mocker.patch(func, return_value=b"")
    success = btm.test_worker("zbl", "zbl")
    assert success

    print("Worker test fail")
    mocker.patch(func, return_value=b"error")
    success = btm.test_worker("zbl", "zbl")
    assert not success


def test_verify_worker(mocker):
    """Test full pipeline of worker testing."""
    with cd(mirror.parent):
        assert BuildTestManager(verbose=True).verify_worker(mirror.name)
