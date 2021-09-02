"""Copyright (C) Alpine Intuition Sàrl - All Rights Reserved.

This source code is protected under international copyright law. All rights
reserved and protected by the copyright holders.
This file is confidential and only available to authorized individuals with the
permission of the copyright holders. If you encounter this file and do not have
permission, please contact the copyright holders and delete this file.
"""
import json
import logging
import re
import tempfile
from pathlib import Path
from typing import Optional, Union

import docker
import enlighten
from archipel_utils import sanitize_inputs

log = logging.getLogger(__name__)


class BuildTestManager:
    """This class is used to build models and test them in a minimal fashion to be sure they run on isquare.ai."""

    def __init__(self, verbose: bool = False):
        self.default_args_hash = "e3b0c442"
        self.verbose = verbose
        self.client = docker.from_env()

        if verbose:
            log.setLevel(logging.DEBUG)

    def build_docker_img(
        self,
        tag: str,
        additional_args: dict = {},
    ):
        client = docker.APIClient(base_url="unix://var/run/docker.sock")

        log.debug(f"Building log for '{tag}'")

        try:
            generator = client.build(path=str(Path.cwd()), tag=tag, **additional_args)
            output = generator.__next__()
        except docker.errors.APIError as error:
            raise docker.errors.BuildError(reason=error.explanation, build_log=error)

        output = json.loads(output.decode())

        # Setup progress bar
        num_steps = int(output["stream"].split()[1].split("/")[-1])
        pbar_args = {"total": num_steps, "unit": "steps"}
        if self.verbose:
            manager = enlighten.get_manager()
            pbar = manager.counter(**pbar_args)
        else:
            pbar = enlighten.Counter(**pbar_args)

        stream = re.sub(r" +", " ", output["stream"].strip())
        logs = [stream]
        log.debug(stream)
        pbar.update()

        while True:
            try:
                output = generator.__next__()
                output = json.loads(output.decode())

                if "stream" in output:
                    stream = re.sub(r" +", " ", output["stream"].strip())
                    if stream != "":
                        log.debug(stream)
                        logs.append(stream)
                        if "Step" in stream:
                            pbar.update()
                elif "errorDetail" in output:  # pragma: no cover
                    # print last message showing the error
                    for log_ in logs:
                        log.info(log_)
                    msg = output["errorDetail"]["message"]
                    raise docker.errors.BuildError(
                        reason=stream if stream != "" else msg, build_log=msg
                    )

            except StopIteration:
                log.debug("Docker image build complete.")
                break

            finally:
                if self.verbose:
                    manager.stop()

        return self.client.images.get(tag).id.split(":")[-1]

    def build_task(
        self,
        script: Union[Path, str],
        task_name: Optional[str] = None,
        dockerfile: Optional[Union[str, Path]] = None,
        cpu: bool = False,
        no_cache: bool = False,
        build_args: str = None,
    ):

        script = Path(script)
        if not script.is_file():
            raise FileNotFoundError(
                "Given script does not exist in build context ({Path.cwd()}): {script}"
            )

        # Setup task name, if none provided just take the script name

        if task_name is None:
            task = script.stem
        else:
            task = sanitize_inputs(task_name)

        log.info(f"Building task '{task}'...")

        task_class_name = self.get_worker_class_name(script)

        # Build docker img

        log.info("Docker image creation")

        cwd = Path.cwd()
        log.info(f"Build context: {cwd}")

        # Check if a dockerfile is given or available (base name 'Dockerfile'). If not
        # use the archipe base one (depending on device detected before). In both case,
        # we use a temporary file to store dockerfile content in order to add our needed
        # commands.

        if dockerfile is None:
            dockerfile = script.parent / "Dockerfile"
            if dockerfile.is_file():
                with open(dockerfile, "r") as f:
                    content = f.read()
            else:
                log.info("No Dockerfile in direct build context, use base image")
                img = "alpineintuition/archipel-base-cpu"
                content = f"FROM {img}\n"
        else:
            dockerfile = Path(dockerfile)
            if str(cwd) not in str(dockerfile.resolve()):
                raise ValueError(
                    f"Provided Dockerfile is not in the build context ({cwd})"
                )
            if not dockerfile.is_file():
                raise FileNotFoundError(f"Invalid file provided: {dockerfile}")
            with open(dockerfile, "r") as f:
                content = f.read()

        if cpu and dockerfile.is_file():
            log.warning(
                "Dockerfile provided but cpu mode argument given. "
                + "Dockerfile has priority, cpu mode argument ignored."
            )

        tmp_dockerfile = tempfile.NamedTemporaryFile()
        tmp_dockerfile_path = tmp_dockerfile.name

        tmp_dockerfile.write(content.encode())
        tmp_dockerfile.write(f"\nCOPY {script} /opt/archipel/worker_script.py".encode())
        tmp_dockerfile.seek(0)

        docker_tag = f"alpineintuion/archipel-task-{task}:latest"

        additional_args = {"dockerfile": tmp_dockerfile_path, "nocache": no_cache}
        if build_args is not None:
            buildargs = {}
            for index, build_arg in enumerate(build_args):
                splitted_build_arg = build_arg.split("=")
                if len(splitted_build_arg) != 2:
                    raise ValueError(
                        f"Invalid format for build args {index}. "
                        + f"Need to look like 'ARGUMENT=VALUE'. Got: {build_arg}"
                    )
                buildargs[splitted_build_arg[0]] = splitted_build_arg[1]
            additional_args["buildargs"] = buildargs

        try:
            docker_img_hash = self.build_docker_img(docker_tag, additional_args)
        finally:
            # if build failed, be sure temp file is close and removed
            tmp_dockerfile.close()

        log.info(f"Task '{task}' successfully built! (docker tag: {dockerfile})")

        return task, docker_img_hash, task_class_name

    def get_worker_class_name(self, script):
        """Get the worker class name.

        Verify script & get class name. We cannot import the file since it can
        contains unknow packages for the host system so we have to parse the file.
        """

        with open(script, "r") as f:
            field = "__task_class_name__"
            worker_class_names = [li for li in f.readlines() if field in li]
            if len(worker_class_names) == 0:
                raise AttributeError(f"There is no '{field}' defined into {script}")
            if len(worker_class_names) > 1:
                raise AttributeError(f"Multiple definitions of '{field}' into {script}")

        worker_class_name = worker_class_names[0].split("=")[-1].strip()
        return re.sub("[^A-Za-z0-9_]+", "", worker_class_name)

    def test_worker(self, img_name, worker_class):
        """Test the forward pass of a built worker."""

        log.info("Testing the worker")

        try:
            cmd = (
                f"python -c 'from worker_script import {worker_class}; "
                + f"{worker_class}().unit_testing()'"
            )
            logs = self.client.containers.run(img_name, cmd, stderr=True)

        except docker.errors.APIError as error:
            raise RuntimeError(f"Error while unit testing worker: {error}")

        except docker.errors.ContainerError as error:
            log.error(f"There was a problem during the tests: \n{error}")
            return False

        if logs != b"":
            log.info(f"Worker starting logs:\n{logs.decode()}")
        log.info("Worker test successful!")

        return True

    def verify_worker(
        self,
        script: Union[Path, str],
        task_name: Optional[str] = None,
        dockerfile: Optional[Union[str, Path]] = None,
        cpu: bool = False,
        no_cache: bool = False,
        build_args: str = None,
    ):

        _, cont_name, class_name = self.build_task(
            script, task_name, dockerfile, cpu, no_cache, build_args
        )
        return self.test_worker(cont_name, class_name)
