"""Copyright (C) Square Factory SA - All Rights Reserved.

This source code is protected under international copyright law. All rights
reserved and protected by the copyright holders.
This file is confidential and only available to authorized individuals with the
permission of the copyright holders. If you encounter this file and do not have
permission, please contact the copyright holders and delete this file.
"""

import click

from i2_client.build import BuildManager


@click.command()
@click.argument("script", type=click.Path(exists=True), required=True)
@click.option(
    "-df",
    "--dockerfile",
    type=click.Path(exists=True),
    help="Name of the Dockerfile. If none provided, base image is used.",
)
@click.option(
    "-nc",
    "--no-cache",
    is_flag=True,
    help="Do not use previous cache when building the image",
)
@click.option(
    "-t",
    "--tag",
    type=str,
    default=None,
    help="Name and optionally a tag in the 'name:tag' format",
)
@click.option(
    "--cpu",
    is_flag=True,
    help="Force the use of CPU base image when no dockerfile available",
)
@click.option(
    "-ba",
    "--build-args",
    type=str,
    default=None,
    multiple=True,
    help="Set build-time variables, like in docker",
)
@click.option(
    "--debug",
    is_flag=True,
    help="Increase logging verbosity level to debug",
)
def build(script, dockerfile, build_args, tag, cpu, no_cache, debug):
    """Build an docker image ready for isquare."""
    BuildManager(debug).build_task(script, dockerfile, build_args, tag, cpu, no_cache)


@click.command()
@click.argument("tag", type=str, required=True)
@click.option(
    "--debug",
    is_flag=True,
    help="Increase logging verbosity level to debug",
)
def test(tag, debug):
    """Verify that an docker image matches the isquare standard."""
    BuildManager(debug=debug).verify_task(tag)
