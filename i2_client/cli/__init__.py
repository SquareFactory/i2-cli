"""Copyright (C) Alpine Intuition Sàrl - All Rights Reserved.

This source code is protected under international copyright law. All rights
reserved and protected by the copyright holders.
This file is confidential and only available to authorized individuals with the
permission of the copyright holders. If you encounter this file and do not have
permission, please contact the copyright holders and delete this file.
"""

import logging

import click
from click.core import Context

from .client import infer
from .worker_tester import test


def create_cli():
    """Create CLI with all sub commands."""

    @click.group()
    @click.option("--verbose", is_flag=True, help="Increase logging depth")
    @click.pass_context
    def archipel_client_cli(ctx: Context, verbose: bool):
        """Command line interface for isquare."""
        ctx.ensure_object(dict)
        ctx.obj["VERBOSE"] = verbose

        logformat = "%(asctime)s - %(levelname)s - %(message)s"
        loglevel = logging.DEBUG if verbose else logging.INFO
        logging.basicConfig(format=logformat, level=loglevel, datefmt="%H:%M:%S")
        # remove anoying logs
        for package in ["docker", "urllib3", "websockets"]:
            logging.getLogger(package).propagate = False

    archipel_client_cli.add_command(test)
    archipel_client_cli.add_command(infer)

    return archipel_client_cli
