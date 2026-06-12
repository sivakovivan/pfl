import pfl


def test_package_exposes_version() -> None:
    assert pfl.__version__ == "0.1.0"
