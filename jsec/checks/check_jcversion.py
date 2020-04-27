import pytest
import os

from pathlib import Path
from jsec.jsec.settings import get_project_root

import subprocess

DATA_DIR = Path(get_project_root() / "data")
