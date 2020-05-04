from jsec.utils import load_versions


# FIXME depends on external configuration
def test__load_versions__filters_unknown_versions():
    versions = ["not a version", "jc221"]
    assert load_versions(versions) == ["jc221"]


def test__load_versions__sorts_versions_from_newest():
    versions = ["jc221", "jc305u3"]
    assert load_versions(versions) == ["jc305u3", "jc221"]
