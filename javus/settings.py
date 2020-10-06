import os
import platform
import shutil
from pathlib import Path


def in_docker():
    r"""Based on answer from: https://stackoverflow.com/a/20012536
    """
    docker = False
    # TODO technically we won't ever be inside Windows container, therefore
    # we only need to check for "Linux" systems
    if platform.system() == "Linux":
        with open("/proc/1/cgroup", "r") as f:
            for line in f.readlines():
                if "docker" in line:
                    docker = True
    return docker


def get_project_root():
    # kudos to https://stackoverflow.com/a/53465812/2377489
    relative_root = Path(__file__).parent.parent
    return relative_root


def get_project_src():
    return get_project_root() / "javus"


def get_project_data():
    return get_project_src() / "data"


def get_project_lib():
    # TODO ponder some more on the fact, that lib resides in src
    return get_project_src() / "lib"


def get_project_attacks():
    return get_project_data() / "attacks"


def get_project_testdir():
    return get_project_root() / "tests"


def get_project_checkdir():
    return get_project_root() / "checks"


def get_viewer_static():
    return get_project_src() / "static"


def get_viewer_templates():
    return get_project_src() / "templates"


def get_registry_file():
    # FIXME this is awful and fragile workaround
    project_registry = get_project_data() / "registry.ini"
    if in_docker():
        docker_registry = Path("/registry/registry.ini")
        if not docker_registry.exists():
            shutil.copyfile(project_registry, docker_registry)
        return docker_registry
    else:
        return project_registry


PROJECT_ROOT = get_project_root()
PROJECT_SRC = get_project_src()
DATA = get_project_data()
LIB_DIR = get_project_lib()
ATTACKS = get_project_attacks()
TESTDIR = get_project_testdir()
CHECKDIR = get_project_checkdir()
STATIC_DIR = get_viewer_static()
TEMPLATES_DIR = get_viewer_templates()
SUBMODULES_DIR = get_viewer_templates()
REGISTRY_FILE = get_registry_file()
