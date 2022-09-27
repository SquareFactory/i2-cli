"""Copyright (C) Square Factory SA - All Rights Reserved.

This source code is protected under international copyright law. All rights
reserved and protected by the copyright holders.
This file is confidential and only available to authorized individuals with the
permission of the copyright holders. If you encounter this file and do not have
permission, please contact the copyright holders and delete this file.
"""
import json
from pathlib import Path, PosixPath
from typing import Union

import cv2
import numpy as np


def open_file(file: Union[str, PosixPath]) -> Union[str, np.ndarray, dict]:
    """Opens any file before sending to an archipel.

    Currently supported files: Text (.txt), JSON (.json) and images (.png,.jpeg & .jpg).

    Args:
        file: The path of the file to open.

    Returns:
        The contents of the file, the format depending on the file type.

    Raises:
        FileNotFoundError: Invalid file path specified.
        RuntimeError: Unsupportted file extension.

    """
    if isinstance(file, PosixPath):
        file = str(file)
    if not Path(file).exists():
        raise FileNotFoundError("The file does not seem to exist.")
    img_extensions = [".png", ".jpeg", ".jpg"]
    suffix = Path(file).suffix
    if suffix in img_extensions:
        return cv2.imread(file)
    elif suffix == ".txt":
        with open(file) as f:
            content = f.read()
        return content
    elif suffix == ".json":
        with open(file) as f:
            content = json.load(f)
        return content
    else:
        raise RuntimeError("Invalid file format specified.")


def save_file(data: Union[str, np.ndarray, dict], path: Union[str, PosixPath]) -> None:
    """Save a file in any format.

    Currently supported files: Text (.txt), JSON (.json) and images (.png,.jpeg & .jpg).

    Args:
        data: Input data, can be string, dictionnary or image in numpy array form.
        path: Path to save the input data.

    Returns:
        None. Saves the data to a file.

    Raises:
        RuntimeError: Unsupported extension or invalid datatype/extension combination.
    """
    if isinstance(path, PosixPath):
        path = str(path)
    suffix = Path(path).suffix
    if suffix not in [".png", ".jpeg", ".jpg", ".txt", ".json"]:
        raise RuntimeError("Invalid file extension specified")
    if suffix == ".txt":
        with open(path, "w") as f:
            f.write(str(data))
    elif suffix == ".json" and isinstance(data, dict):
        with open(path, "w") as f:
            json.dump(data, f)
    elif suffix in [".png", ".jpeg", ".jpg"] and isinstance(data, np.ndarray):
        cv2.imwrite(path, data)
    else:
        if suffix in [".png", ".jpeg", ".jpg", ".txt", ".json"]:
            raise RuntimeError(
                "Specified output format and extension do not match with data type."
            )
