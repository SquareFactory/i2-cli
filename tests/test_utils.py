"""Copyright (C) Square Factory SA - All Rights Reserved.

This source code is protected under international copyright law. All rights
reserved and protected by the copyright holders.
This file is confidential and only available to authorized individuals with the
permission of the copyright holders. If you encounter this file and do not have
permission, please contact the copyright holders and delete this file.
"""

import tempfile
from pathlib import Path

import cv2
import numpy as np
import pytest

from i2_client.utils import open_file, save_file


def test_open_save_file():
    """Test file saving and loading."""
    with pytest.raises(FileNotFoundError):
        open_file("zbeul")

    with pytest.raises(RuntimeError):
        open_file("tests/test_utils.py")

    with pytest.raises(RuntimeError):
        save_file("Hello world", "zbeul.zbl")

    with pytest.raises(RuntimeError):
        save_file({"hello": "world"}, "hw.png")

    # create dir to store inputs
    dir = tempfile.TemporaryDirectory()
    dirpath = Path(dir.name)
    dump_img = cv2.imread("examples/test.jpg")
    save_file("hello world", dirpath / "hw.txt")
    save_file({"hello": "world"}, dirpath / "hw.json")

    save_file(dump_img, dirpath / "hw.png")
    save_file(dump_img, dirpath / "hw.jpg")
    save_file(dump_img, dirpath / "hw.jpeg")

    assert open_file(dirpath / "hw.txt") == "hello world"
    assert open_file(dirpath / "hw.json") == {"hello": "world"}
    assert np.array_equal(open_file(dirpath / "hw.png"), dump_img)
    # the following have different compression and are therefore only checked for shape.
    assert open_file(dirpath / "hw.jpg").shape == dump_img.shape
    assert open_file(dirpath / "hw.jpeg").shape == dump_img.shape
