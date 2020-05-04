from pathlib import Path
import os


def get_project_root():
    # kudos to https://stackoverflow.com/a/53465812/2377489
    # first try to read the environemnt variable
    env_root = Path(os.getenv("JCVM_ANALYSIS_HOME"))
    relative_root = Path(__file__).parent.parent

    if env_root:
        # prefer user specified value in case of conflict
        if env_root != relative_root:
            return env_root
    return relative_root


def get_project_src():
    return get_project_root() / "jsec"


def get_project_data():
    return get_project_src() / "data"


def get_project_lib():
    # TODO ponder some more on the fact, that lib resides in src
    return get_project_src() / "lib"


PROJECT_ROOT = get_project_root()
PROJECT_SRC = get_project_src()
DATA = get_project_data()
LIB_DIR = get_project_lib()
