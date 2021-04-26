"""Script that does final markdown formatting 
   after argdown parse_args to markdown conversion
   
   Note:
   It is recognized that this is a horrible way to do things.
   We'll use this until an arg parser extension is available 
   for mkdocs.
"""

import re

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
            newline = newline.replace('!!!\n', '!!! ')
            newline = newline.replace('&nbsp;&nbsp;&nbsp;&nbsp;', '\n    ')
            newline = newline.replace('```', '\n```\n')
            newline = newline.replace(':  \n', ':  \n\n')
            newline = newline.replace(']:\n', ']: ')
            newline = newline.replace('\n*\n','\n* ')
            newlines.append(newline)
    all_lines = ''.join(newlines)
    # fix code blocks from argdown
    # first remove all line breaks
    # and add valid ones afterwards
    pat = r'```(.*?)```'
    regex = re.compile(pat, re.DOTALL|re.MULTILINE)
    # get number of total matches
    match_count = len([x for x in re.finditer(regex, all_lines)])
    for match_x in range(match_count-1):
        for x, match in enumerate(re.finditer(regex, all_lines)):
            if x == 0:
                # skip first code blocks
                # with index
                continue
            if x != match_x+1:
                continue
            # Start index of match (integer)
            sStart = match.start()
        
            # Final index of match (integer)
            sEnd = match.end()
            
            # Complete match (string)
            sGroup = match.group().replace(
                '\n'," ").replace(
                    '  ',"\n").replace(
                                '``` ','```').replace(
                                    '-- ','--').replace(
                                        '```bash',"```bash\n").replace(
                                            '```python',"```python\n").replace(
                                                '```sql',"```sql\n").replace(
                                                    '\n ',"\n").replace(
                                                        '\n\n',"\n")
            all_lines="".join((all_lines[:sStart],sGroup,all_lines[sEnd:]))
            # Print match
            # print('Match "{}" found at: [{},{}]'.format(sGroup, sStart,sEnd))  
    # cleanup
    with open("docs/argparse/args.md", "w") as source_file:
        source_file.write(all_lines)

# run script
format_markdown()
