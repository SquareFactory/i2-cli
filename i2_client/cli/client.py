"""Copyright (C) Square Factory SA - All Rights Reserved.

This source code is protected under international copyright law. All rights
reserved and protected by the copyright holders.
This file is confidential and only available to authorized individuals with the
permission of the copyright holders. If you encounter this file and do not have
permission, please contact the copyright holders and delete this file.
"""


import click
import numpy as np

from i2_client.client import I2Client
from i2_client.utils import open_file, save_file


@click.command()
@click.argument(
    "data",
    type=click.Path(exists=True),
    required=True,
)
@click.option("--url", type=str, required=True, help="url given by isquare.")
@click.option(
    "--access-key", type=str, required=True, help="Access key provided by isquare."
)
@click.option(
    "--save-path", type=str, help="Path to save your data (img, txt or json)."
)
@click.option(
    "--debug",
    is_flag=True,
    help="Increase logging verbosity level to debug",
)
def infer(data, url, access_key, save_path, debug):  # pragma: no cover
    """Send data for inference."""

    client = I2Client(url, access_key, debug)

    content = open_file(data)
    output = client.inference(content)

    if save_path is not None:
        save_file(output, save_path)
    else:
        if not isinstance(output, np.ndarray):
            print(output)
        else:
            try:
                import cv2

                cv2.imshow(output)
            except ImportError:
                print("`cv2` module not available, can not show inference.")
