"""Script to allow argdown parse_args to markdown conversion"""

import inspect
from lbsntransform import BaseConfig
from lbsntransform import __version__


def extract_argscode():
    """Extracts command line args code to separate file

    Preparation step for processing with argdown
    """
    # open file to output source code
    source_file = open("parse_args.py", "w")
    # extract source code of parse_args
    parse_args_source = inspect.getsource(BaseConfig.get_arg_parser)
    # remove first three lines
    for __ in range(0, 3):
        parse_args_source = parse_args_source[parse_args_source.index("\n") + 1 :]
    # insert at beginning
    parse_args_source = (
        f'parser = argparse.ArgumentParser(prog="lbsntransform")\n{parse_args_source}'
    )
    # unindent all other lines
    parse_args_source = parse_args_source.lstrip().replace("\n        ", "\n")
    # replace version string
    parse_args_source = parse_args_source.replace(
        "{__version__}", f"{__version__}"
    )
    # replace package name
    parse_args_source = parse_args_source.replace(
        "usage: argdown", "usage: lbsntransform"
    )
    # write argdown and argparse imports first
    source_file.write("import argparse\n")
    source_file.write("import argdown\n")
    source_file.write("from pathlib import Path\n")
    # fix argparse name
    parse_args_source = parse_args_source.replace(
        "ArgumentParser()", 'ArgumentParser(prog="lbsntransform")'
    )
    # replace method leftover
    parse_args_source = parse_args_source.replace(
        "return parser", "args = parser.parse_args()"
    )
    # replace two empty spaces on str line ends with non-breaking spaces,
    # protecting line breaks during python-markdown conversion
    parse_args_source = parse_args_source.replace("'  '\n", "'&nbsp;&nbsp;<br>'\n")
    parse_args_source = parse_args_source.replace("  '\n", "&nbsp;&nbsp;<br>'\n")
    # protected indent
    parse_args_source = parse_args_source.replace("'    ", "'&nbsp;&nbsp;&nbsp;&nbsp;")
    # write prepared source code
    source_file.write(parse_args_source)
    source_file.close()


# run script
extract_argscode()
