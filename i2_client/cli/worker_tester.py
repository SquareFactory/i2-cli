"""Copyright (C) Alpine Intuition Sàrl - All Rights Reserved.

This source code is protected under international copyright law. All rights
reserved and protected by the copyright holders.
This file is confidential and only available to authorized individuals with the
permission of the copyright holders. If you encounter this file and do not have
permission, please contact the copyright holders and delete this file.
"""

import click
from click import Context

from i2_client.worker_tester import BuildTestManager


@click.group()
@click.pass_context
def test(ctx: Context):
    """Test the build of your worker before uploading to isquare."""
    ctx.ensure_object(dict)
    ctx.obj["BUILD_TEST_MANAGER"] = BuildTestManager(ctx.obj["VERBOSE"])


@test.command("worker")
@click.pass_context
@click.argument("task_script", type=click.Path(exists=True), required=True)
@click.option(
    "--dockerfile", type=click.Path(exists=True), help="Provide a dockerfile path"
)
@click.option("--task_name", type=str, default=None)
@click.option("--cpu", is_flag=True, help="Force only CPU mode")
@click.option("--no-cache", is_flag=True, help="Do not use cached files for build")
def worker(ctx: Context, task_script: str, task_name, dockerfile, cpu, no_cache):
    """Test the build and logic of a worker before deploying on archipel."""
    ctx.obj["BUILD_TEST_MANAGER"].verify_worker(
        task_script, task_name, dockerfile, cpu, no_cache
    )
