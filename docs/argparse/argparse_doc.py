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
    parse_args_source = inspect.getsource(BaseConfig.parse_args)
    # remove first line
    parse_args_source = parse_args_source[parse_args_source.index('\n')+1:]
    # unindent all other lines
    parse_args_source = parse_args_source.lstrip().replace('\n        ', '\n')
    # replace version string
    parse_args_source = parse_args_source.replace(
        'lbsntransform {__version__}', f'lbsntransform {__version__}')
    # replace package name
    parse_args_source = parse_args_source.replace(
        'usage: argdown', 'usage: lbsntransform')
    # write argdown and argparse imports first
    source_file.write('import argparse\n')
    source_file.write('import argdown\n')
    source_file.write('from pathlib import Path\n')
    source_file.write('from lbsntransform import BaseConfig\n')
    # fix argparse name
    parse_args_source = parse_args_source.replace(
        'ArgumentParser()', 'ArgumentParser(prog="lbsntransform")')
    # replace two empty spaces on str line ends with non-breaking spaces,
    # protecting line breaks during python-markdown conversion
    parse_args_source = parse_args_source.replace(
        "'  '\n", "'&nbsp;&nbsp;<br>'\n")
    parse_args_source = parse_args_source.replace(
        "  '\n", "&nbsp;&nbsp;<br>'\n")
    # protected indent
    parse_args_source = parse_args_source.replace(
        "'    ", "'&nbsp;&nbsp;&nbsp;&nbsp;")
    # write prepared source code
    source_file.write(parse_args_source)
    source_file.close()


# run script
extract_argscode()
