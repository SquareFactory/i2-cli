"""Copyright (C) Square Factory SA - All Rights Reserved.

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
from rich.progress import Progress

log = logging.getLogger("i2-build")


class BuildManager:
    """i2 build manager."""

    def __init__(self, debug: bool = False):
        """Initialize build manager.

        Args:
            debug: Optional; Show extensive logs.

        Returns:
            None.

        Raises:
            None.
        """

        self.client = docker.from_env()

        if debug:
            log.setLevel(logging.DEBUG)

    def _get_worker_class_name(self, content):
        """Get the worker class name.

        Verify script & get class name. We cannot import the file since it can
        contains unknow packages for the host system so we have to parse the file.
        """

        field = "__task_class_name__"
        worker_class_names = [li for li in content if field in li]

        if len(worker_class_names) == 0:
            raise AttributeError(f"Missing field in given script: {field}")
        if len(worker_class_names) > 1:
            raise AttributeError(f"Multiple field definitions given script: {field}")

        worker_class_name = worker_class_names[0].split("=")[-1].strip()
        worker_class_name = worker_class_name.replace('"', "").replace("'", "")

        sanatized = re.sub("[^A-Za-z0-9_]+", "", worker_class_name)
        if worker_class_name != sanatized:
            raise ValueError(
                f"'{field}' must not contain any special characters: {sanatized}"
            )

        return worker_class_name

    def _build_docker_img(
        self,
        tag: str,
        additional_args: dict = {},
    ):
        """Build the docker image for a worker in current dir.

        Args:
            tag: The tag for the image to build.
            additional_args: Optional; Additional arguments for the build.

        Returns:
            The tag of the built docker image.

        Raises:
            docker.errors.BuildError: There was an error during the build (the specific error is printed).

        """

        client = docker.APIClient(base_url="unix://var/run/docker.sock")

        log.info(f"Building '{tag}'...")

        try:
            generator = client.build(path=str(Path.cwd()), tag=tag, **additional_args)
            output = generator.__next__()
        except docker.errors.APIError as error:
            raise docker.errors.BuildError(reason=error.explanation, build_log=error)

        output = json.loads(output.decode())

        # Setup progress bar
        num_steps = int(output["stream"].split()[1].split("/")[-1])

        with Progress(transient=True) as progress:
            task = progress.add_task("Building...", total=num_steps)

            stream = re.sub(r" +", " ", output["stream"].strip())
            log.info(f"[bold][DOCKER SDK LOG][/bold] {stream}")
            progress.update(task, advance=1)

            while True:
                try:
                    output = generator.__next__()
                    output = json.loads(output.decode())

                    if "stream" in output:
                        stream = re.sub(r" +", " ", output["stream"]).replace("\n", "")
                        if stream != "":
                            # remove colors so no issues when printing in console
                            colorless_stream = stream.replace("[91m", "").replace(
                                "[0m", ""
                            )
                            log.info(
                                f"[bold][DOCKER SDK LOG][/bold] {colorless_stream}"
                            )
                            if "Step" in stream:
                                progress.update(task, advance=1)

                    elif "errorDetail" in output:  # pragma: no cover
                        msg = output["errorDetail"]["message"]
                        reason = stream if stream != "" else msg
                        raise docker.errors.BuildError(reason=reason, build_log=msg)

                except StopIteration:
                    break

        log.info("Building ended successfully!")

        return self.client.images.get(tag).id.split(":")[-1]

    def _test_task(self, docker_img, worker_class):
        """Test the forward pass of a built worker.

        Args:
            docker_img: Name of the docker image to test.
            worker_class: Name of the worker python class.

        Returns:
            None.

        Raises:
            RuntimeError: There was a problem with docker during the tests.
        """

        log.info("Testing...")

        try:
            cmd = (
                f"python -c 'from worker_script import {worker_class}; "
                + f"{worker_class}().unit_testing()'"
            )
            logs = self.client.containers.run(docker_img, cmd, stderr=True)

        except docker.errors.APIError as error:
            raise RuntimeError(f"Error while task unit testing: \n{error}")

        except docker.errors.ContainerError as error:
            raise RuntimeError(f"There was a problem during the tests: \n{error}")

        if logs != b"":
            log.info(f"Starting logs:\n\n{logs.decode()}")

        log.info("Testing ended successfully!")

    def build_task(
        self,
        script: Union[Path, str],
        dockerfile: Optional[Union[str, Path]] = None,
        build_args: str = None,
        docker_tag: str = None,
        cpu: bool = False,
        no_cache: bool = False,
    ):
        """Build an archipel task.

        Args:
            script: The worker script.
            dockerfile: Optional; Name of the Dockerfile. If none provided, base
                image is used.
            build_args: Optional; Set build-time variables, like in docker.
            docker_tag: Optional; Name and optionally a tag in the 'name:tag' format.
            cpu: Optional; Force the use of CPU base image when no dockerfile available.
            no_cache: Optional; Do not use previous cache when building the image.

        Returns:
            None.

        Raises:
            ValueError: Invalid Dockerfile contents or build arguments.
            FileNotFoundError: Invalid locaiton specified for script or Dockerfile.
        """

        cwd = Path.cwd()

        script = Path(script)
        if not script.is_file():
            raise FileNotFoundError(f"File not found: {script} (build context: {cwd})")

        # Setup task name, if none provided just take the script name

        log.info(f"Building task from '{script}'...")

        task_name = script.stem

        with open(script, "r") as f:
            worker_class_name = self._get_worker_class_name(f.readlines())
        log.debug(f"Worker class: {worker_class_name}")

        # Build docker img

        log.debug(f"Build context: {cwd}")

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
                device = "cpu" if cpu else "gpu"
                log.info(f"No Dockerfile found, use {device.upper()} base image")
                img = f"alpineintuition/archipel-base-{device}"
                content = f"FROM {img}\n"
        else:
            dockerfile = Path(dockerfile)
            if str(cwd) not in str(dockerfile.resolve()):
                raise ValueError(
                    f"Provided Dockerfile ({dockerfile}) does not exist "
                    + f"in build context ({cwd})"
                )
            if not dockerfile.is_file():
                raise FileNotFoundError(
                    f"Provided dockerfile does not exist: {dockerfile}"
                )
            with open(dockerfile, "r") as f:
                content = f.read()

        if cpu and dockerfile.is_file():
            log.warning(
                "Dockerfile available but cpu mode argument given. "
                + "Dockerfile has priority, cpu mode argument ignored."
            )

        tmp_dockerfile = tempfile.NamedTemporaryFile()
        tmp_dockerfile_path = tmp_dockerfile.name

        tmp_dockerfile.write(content.encode())
        tmp_dockerfile.write(f"\nCOPY {script} /opt/archipel/worker_script.py".encode())
        tmp_dockerfile.seek(0)

        docker_tag = f"i2-task-{task_name}:latest" if docker_tag is None else docker_tag

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
            self._build_docker_img(docker_tag, additional_args)
        finally:
            # if build failed, be sure temp file is close and removed
            tmp_dockerfile.close()

        self._test_task(docker_tag, worker_class_name)

        log.info(f"Building and testing done! (docker tag: '{docker_tag}')")

    def verify_task(self, docker_tag):
        """Verify that a built docker image is valid.

        Args:
            docker_tag: Name of the docker image to test.

        Returns:
            None.

        Raises:
            RuntimeError: There was a problem with docker during the tests.
        """
        try:
            cmd = "cat /opt/archipel/worker_script.py".split()
            out = self.client.containers.run(docker_tag, cmd, stderr=True)
            worker_class_name = self._get_worker_class_name(out.decode().split("\n"))
            log.debug(f"Worker class name: {worker_class_name}")

        except docker.errors.ImageNotFound:
            raise RuntimeError(f"Image not found: {docker_tag}")

        except docker.errors.ContainerError as error:
            msg = error.stderr.decode()
            raise RuntimeError(f"Error when trying to detect class name: \n {msg}")

        self._test_task(docker_tag, worker_class_name)
