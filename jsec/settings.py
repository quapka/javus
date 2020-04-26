from pathlib import Path

# kudos to https://stackoverflow.com/a/53465812/2377489
def get_project_root():
    """Returns project root folder."""
    return Path(__file__).parent.parent
