from invoke import task
import os
from contextlib import contextmanager
import logging


# TODO add logging, might require setting flags through tasks
# log = logging.getLogger(__file__)
# handler = logging.StreamHandler()
# formatter = logging.Formatter("%(levelname)s:%(asctime)s:%(name)s: %(message)s")
# handler.setFormatter(formatter)
# log.addHandler(handler)


def get_project_root():
    this_file = os.path.realpath(__file__)
    return os.path.dirname(this_file)


PROJECT_ROOT = get_project_root()


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
def test(c):
    cmd = []
    if not pipenv_is_active():
        cmd += ["pipenv", "run"]

    cmd += ["pytest", "-v", "-c", "tests/pytest.ini", "tests"]
    with cd(PROJECT_ROOT):
        c.run(" ".join(cmd), pty=True)


@task
def check(c):
    cmd = []
    if not pipenv_is_active():
        cmd += ["pipenv", "run"]

    cmd += ["pytest", "-v", "-c", "checks/check.ini", "checks"]
    with cd(PROJECT_ROOT):
        c.run(" ".join(cmd), pty=True)
