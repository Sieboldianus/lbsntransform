"""Script that does final markdown formatting 
   after argdown parse_args to markdown conversion
"""

def format_markdown():
    """Final markdown formatting fixes
    """
    # open file to output source code
    source_file_path = "docs/argparse/args.md"
    # fix markdown linebreaks from python docstrings convert
    newlines = []
    with open(source_file_path, "r") as source_file:
        for line in source_file:
            newline = line.replace('&nbsp;&nbsp;<br>', '  \n')
            newline = newline.replace(':  \n', ':  \n\n')
            newline = newline.replace(']:\n', ']: ')
            newline = newline.replace('\n*\n','\n* ')
            newlines.append(newline)
    with open("docs/argparse/args.md", "w") as source_file:
        for line in newlines:
            source_file.write(line)

# run script
format_markdown()
