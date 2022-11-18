import logging
import os
import pathlib
import sys
from contextlib import contextmanager

from invoke import task

# TODO add logging, might require setting flags through tasks
# log = logging.getLogger(__file__)
# handler = logging.StreamHandler()
# formatter = logging.Formatter("%(levelname)s:%(asctime)s:%(name)s: %(message)s")
# handler.setFormatter(formatter)
# log.addHandler(handler)


def get_project_root():
    this_file = pathlib.Path(__file__).resolve()
    return this_file.parent


PROJECT_ROOT = get_project_root()


def git_dirty(c):
    cmd = ["git", "status", "--porcelain"]
    with cd(PROJECT_ROOT):
        proc = c.run(" ".join(cmd))
    return proc.stdout != ""


def pipenv_is_active():
    return os.environ.get("PIPENV_ACTIVE", 0) == "1"


@contextmanager
def cd(new_path):
    """
    kudos to:
    https://stackoverflow.com/questions/431684/how-do-i-change-the-working-directory-in-python/13197763#13197763
    """
    old_path = os.getcwd()
    # log.debug("Save old path: %s", old_path)
    try:
        # log.debug("Change directory to: %s", new_path)
        # # no yield for now, as there is no need for additional information
        os.chdir(new_path)
        yield old_path
    finally:
        # the old directory might also be remove, however there isn't
        # good and logical thing to do, so in that case the exception will be
        # thrown
        # log.debug("Switch back to old path: %s", old_path)
        os.chdir(old_path)


# list of the actual tasks goes here
@task
def test(c, debug=False, verbose=True):
    r"""Run the tests for this project"""
    cmd = []
    if not pipenv_is_active():
        cmd += ["pipenv", "run"]

    cmd += ["pytest"]
    if debug:
        cmd += ["--capture=no"]
    if verbose:
        cmd += ["--verbose"]

    cmd += ["-c", "tests/pytest.ini", "tests"]
    with cd(PROJECT_ROOT):
        c.run(" ".join(cmd), pty=True)
    # TODO add overall success or failure to inform the user


@task
def check(c, debug=False, verbose=True):
    r"""Run the live checks for this project"""
    cmd = []
    if not pipenv_is_active():
        cmd += ["pipenv", "run"]

    cmd += ["pytest"]
    if debug:
        cmd += ["--capture=no"]
    if verbose:
        cmd += ["--verbose"]

    cmd += ["-c", "checks/check.ini", "checks"]
    with cd(PROJECT_ROOT):
        c.run(" ".join(cmd), pty=True)

    # TODO add overall success or failure to inform the user


@task
def todo(c):
    r"""Show the TODOs and FIXMEs in the project"""
    cmd = ["grep", "-ir", r"'FIXME\|TODO'", "*"]

    with cd(PROJECT_ROOT):
        c.run(" ".join(cmd), pty=True)


@task
def develop(c, restart=False):
    r"""Install the project and scripts, so that you can develop
    and test it immediately and easily
    """
    cmd = []
    if not pipenv_is_active():
        cmd += ["pipenv", "run"]

    cmd += ["pip3"]
    if restart:
        uninstall_cmd = cmd + ["uninstall", "--yes", "javus"]
        with cd(PROJECT_ROOT):
            c.run(" ".join(uninstall_cmd))

    install_cmd = cmd + ["install", "--editable", "."]
    with cd(PROJECT_ROOT):
        c.run(" ".join(install_cmd))
    # TODO add overall success or failure to inform the user


@task
def sort_imports(c):
    r"""Use `isort` to fix the Python imports in the whole project"""
    if git_dirty(c):
        print("Repository is dirty! Commit changes.")
        sys.exit(1)
    cmd = ["isort", "--recursive", "--atomic", "."]
    with cd(PROJECT_ROOT):
        c.run(" ".join(cmd))


@task
def dock(c, local=True):
    # TODO probably there should be release and development version of the image
    # TODO rename task to something like build-docker-image
    # but only after tab completion for invoke commands is figure out
    r"""Build the newest docker image"""
    cmd = ["docker", "build", "--tag", "javus-container:latest", "."]
    with cd(PROJECT_ROOT):
        c.run(" ".join(cmd))

    # TODO if local the build copies the local files and does not use git
    # to actual clone the source


@task
def docs(c):
    cmd = []
    if not pipenv_is_active():
        cmd += ["pipenv", "run"]

    cmd += ["make", "html"]
    with cd(PROJECT_ROOT / "docs"):
        c.run(" ".join(cmd))


@task
def update_sdks(c):
    # TODO implement
    # this task updates javus/lib/jcversion.properties
    # according to oracle_javacard_sdks
    pass
