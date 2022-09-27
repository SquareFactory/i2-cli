"""Copyright (C) Square Factory SA - All Rights Reserved.

This source code is protected under international copyright law. All rights
reserved and protected by the copyright holders.
This file is confidential and only available to authorized individuals with the
permission of the copyright holders. If you encounter this file and do not have
permission, please contact the copyright holders and delete this file.
"""

import logging
from pathlib import Path
from tempfile import NamedTemporaryFile

import docker
import pytest

from i2_client.build import BuildManager

mirror = Path("examples/tasks/mirror.py")
mirror_img = f"i2-task-{mirror.stem}:latest"

face_alignment = Path("examples/tasks/face_alignment/face_alignment.py")
face_alignment_dockerfile = Path("examples/tasks/face_alignment/Dockerfile")
face_alignment_img = f"i2-task-{face_alignment.stem}:latest"

client = docker.from_env()


def test_init():
    """Test initialization of BuildManager.

    - With / without debug mode

    """
    BuildManager()
    assert logging.getLogger("i2-build").level == 0  # by default in WARNING

    BuildManager(debug=True)
    assert logging.getLogger("i2-build").level == 10  # in debug mode


def test_get_worker_class_name():
    """Test get worker class name.

    Tested:
        - field not present
        - multiple fields
        - sanitize inputs
    """

    bm = BuildManager()

    print("No valid field into file")
    content = ["no field"]
    with pytest.raises(AttributeError):
        bm._get_worker_class_name(content)

    print("Multiple definitions")
    content = ["__task_class_name__ = 'zbl'", '__task_class_name__ = "zbl"']
    with pytest.raises(AttributeError):
        bm._get_worker_class_name(content)

    print("Sanize inputs")
    content = ["__task_class_name__ = 'zbl_.;l'"]
    with pytest.raises(ValueError):
        bm._get_worker_class_name(content)


def test_build_task(mocker):
    """Test task build.

    - Test build of docker img with and without dockerfile
    - Check if specify tag is used

    """

    def get_docker_imgs():
        imgs = []
        for img in client.images.list():
            imgs += img.tags
        return imgs

    bm = BuildManager()

    print("basic building")
    args = ("VAR=VALUE",)
    bm.build_task(mirror, cpu=True, build_args=args)
    assert mirror_img in get_docker_imgs()

    print("give a specific tag")
    tag = "i2-pytest:latest"
    bm.build_task(mirror, docker_tag=tag, cpu=True, build_args=args)
    assert tag in get_docker_imgs()

    print("build with dockerfile (without specify)")
    bm.build_task(face_alignment)
    assert face_alignment_img in get_docker_imgs()

    print("build with dockerfile (specify)")
    bm.build_task(face_alignment, dockerfile=face_alignment_dockerfile)


def test_build_task_issues(mocker):
    """Test task build issues.

    - Given script does not exist.
    - Given dockerfile does not exist.
    - Invalid build args format.
    - Dockerfile empty
    - Bad command in dockerfile.
    """

    bm = BuildManager()

    print("script do not exist")
    with pytest.raises(FileNotFoundError):
        bm.build_task("zbl")

    print("dockerfile do not exist")
    with pytest.raises(FileNotFoundError):
        bm.build_task(mirror, dockerfile=mirror.parent / "zbl")

    print("dockerfile is not in the build context")
    with pytest.raises(ValueError):
        bm.build_task(mirror, dockerfile="../zbl")

    print("invalid buildargs")
    with pytest.raises(ValueError):
        args = ("VALUE TEST",)
        bm.build_task(mirror, cpu=True, build_args=args)

    print("error in dockerfile: empty file")
    with NamedTemporaryFile(dir=".") as tmp_file:
        with pytest.raises(docker.errors.BuildError):
            bm.build_task(mirror, dockerfile=tmp_file.name)

    print("error in dockerfile: wrong command")
    with NamedTemporaryFile(dir=".") as tmp_file:
        tmp_file.write(b"FROM alpineintuition/archipel-base-cpu:latest")
        tmp_file.write(b"ZBL")
        tmp_file.seek(0)
        with pytest.raises(docker.errors.BuildError):
            bm.build_task(mirror, dockerfile=tmp_file.name)


def test_verify_task_mirror(mocker):
    """Test verify task."""

    bm = BuildManager()

    print("Working unit test")
    bm._test_task(mirror_img, "MirrorWorker")

    print("Wrong class name")
    with pytest.raises(RuntimeError):
        bm._test_task(mirror_img, "ImagesToImagesWorker")

    print("Verify")
    bm.verify_task(mirror_img)

    print("Verify, no image")
    with pytest.raises(RuntimeError):
        bm.verify_task("zbl")
