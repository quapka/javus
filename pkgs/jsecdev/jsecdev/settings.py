import os
from pathlib import Path


def get_project_root() -> Path:
    # kudos to https://stackoverflow.com/a/53465812/2377489
    relative_root = Path(__file__).parent.parent

    return relative_root


def get_project_src() -> Path:
    return get_project_root() / "jsecdev"


def get_project_data() -> Path:
    return get_project_src() / "data"


def get_jsec_attacks_dir() -> Path:
    # FIXME this can break easily, but there isn't seem to be reasonable workaround
    # at the moment
    return get_project_root().parent.parent / "jsec" / "data" / "attacks"


PROJECT_ROOT = get_project_root()
PROJECT_SRC = get_project_src()
DATA = get_project_data()
JSEC_ATTACKS_DIR = get_jsec_attacks_dir()
