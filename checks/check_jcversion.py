import os
import subprocess
from pathlib import Path

import pytest

from javus.settings import get_project_root

DATA_DIR = Path(get_project_root() / "data")
