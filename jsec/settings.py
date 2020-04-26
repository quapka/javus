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
