"""Copyright (C) Alpine Intuition Sàrl - All Rights Reserved.

This source code is protected under international copyright law. All rights
reserved and protected by the copyright holders.
This file is confidential and only available to authorized individuals with the
permission of the copyright holders. If you encounter this file and do not have
permission, please contact the copyright holders and delete this file.
"""
import click
import cv2
import numpy as np
from click import Context

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
@click.option("--save-path", type=str, help="Path to save your data (img,txt or json).")
@click.pass_context
def infer(ctx: Context, data, url, access_key, save_path):  # pragma: no cover
    """Send data for inference."""
    ctx.ensure_object(dict)
    client = I2Client(url, access_key, ctx.obj["VERBOSE"])
    content = open_file(data)
    output = client.inference(content)
    if save_path is not None:
        save_file(output, save_path)
    else:
        if not isinstance(output, np.ndarray):
            print(output)
        else:
            cv2.imshow(output)
