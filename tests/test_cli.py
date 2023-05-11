"""
Tests for command line interface (CLI).
"""
from importlib.metadata import version
from os import linesep

from .cli_test_helpers import shell


def test_version():
    """
    Does --version display information as expected?
    """
    expected_version = version("lbsntransform")
    result = shell("lbsntransform --version")

    assert result.stdout == f"{expected_version}{linesep}"
    assert result.exit_code == 0
