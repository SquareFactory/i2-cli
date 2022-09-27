"""Copyright (C) Square Factory SA - All Rights Reserved.

This source code is protected under international copyright law. All rights
reserved and protected by the copyright holders.
This file is confidential and only available to authorized individuals with the
permission of the copyright holders. If you encounter this file and do not have
permission, please contact the copyright holders and delete this file.
"""

import logging

import click
from rich.logging import RichHandler

from .build import build, test
from .client import infer


def create_cli():
    """Create CLI with all sub commands."""

    @click.group()
    def archipel_client_cli():
        """Command line interface for isquare."""

        rich_handler = RichHandler(
            show_path=False,
            omit_repeated_times=False,
            log_time_format="[%H:%M:%S]",
            markup=True,
        )
        logging.basicConfig(
            format="%(message)s", level=logging.INFO, handlers=[rich_handler]
        )

        # remove anoying logs
        for package in ["docker", "urllib3", "websockets"]:
            logging.getLogger(package).propagate = False

    archipel_client_cli.add_command(build)
    archipel_client_cli.add_command(test)
    archipel_client_cli.add_command(infer)

    return archipel_client_cli
