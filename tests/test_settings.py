import os
from pathlib import Path

from jsec.settings import get_project_root


def test_getting_project_root():
    original = os.getenv("JCVM_ANALYSIS_HOME")
    os.environ["JCVM_ANALYSIS_HOME"] = "test/custom/path that:does:not:exist"

    assert get_project_root() == Path("test/custom/path that:does:not:exist")


# TODO add test for the rest of set paths
