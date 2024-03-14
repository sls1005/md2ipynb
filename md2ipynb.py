#!/usr/bin/env python3
# -*- coding: ASCII -*-
import re
from json import dumps as to_json
from sys import stdout, stderr, argv
from os.path import exists

usage = '''
usage: md2ipynb.py [options] <file>

arguments:
      <file>                                  The name of the input file (a Markdown file).

options:
      -h, --help                              Display this help message and exit.

      -e, --encoding <encoding>               The encoding of the input file.

      -o, --output <file>                     The name of the output file. Usually ends with '.ipynb'.

      -k, --kernel <kernel>                   The kernel to be used by the created notebook. (default: 'python3')

      -lang, --language <language>            The programming language. (default: 'python')

      --language-identifier <identifier>      The identifier used in the input file for syntax highlighting. Default to the language name given with '-lang', or 'python' if none.

      --overwrite                             Overwrite the output file if it exists.
'''

def convert(input_file_name, output_file_name, input_file_encoding = 'UTF-8', output_file_encoding = 'UTF-8', language = 'python', language_identifier = 'python', kernel = 'python3'):
    code_block_start = re.compile("^(\\x20){0,3}```(\\s)*" + language_identifier + "(\\s)*$")
    other_block_start1 = re.compile("^(\\x20){0,3}```")
    other_block_start2 = re.compile("^(\\x20){0,3}````")
    block_end = re.compile("^(\\x20){0,3}```(\\s)*$")
    block_end2 = re.compile("^(\\x20){0,3}````(\\s)*$")
    in_code_block = False
    in_other_block = 0
    in_markdown = False
    at_start = True
    at_start_of_code_block = False
    metadata = {
        'kernelspec': {
            'name': kernel
        },
        'language_info': {
            'name': language
        }
    }
    input_file = open(input_file_name, 'r', encoding=input_file_encoding)
    output_file = open(output_file_name, 'w', encoding=output_file_encoding)
    output_file.write('{"nbformat":%d,"nbformat_minor":%d,"cells":[\n' % (4, 0))
    for line in input_file:
        if in_code_block:
            if block_end.search(line): # != None
                output_file.write('","outputs":[]}')
                in_code_block = False
            else:
                #assert line[-1] == '\n'
                c = ''
                if at_start_of_code_block:
                    at_start_of_code_block = False
                else:
                    c = '\n'
                output_file.write(to_json(c + line[:-1])[1:-1])
        elif code_block_start.search(line) and not in_other_block:
            if in_markdown:
                output_file.write('"}')
                in_markdown = False
            if at_start:
                at_start = False
            else:
                output_file.write(',\n')
            output_file.write('{"cell_type":"code","metadata":{},"source":"')
            in_code_block = True
            at_start_of_code_block = True
        elif in_markdown:
            if in_other_block:
                if [block_end, block_end2][in_other_block - 1].search(line):
                    in_other_block = 0
            else:
                if other_block_start2.search(line):
                    in_other_block = 2
                elif other_block_start1.search(line):
                    in_other_block = 1
            output_file.write(to_json(line)[1:-1])
        else:
            if line == '\n':
                continue
            elif at_start:
                at_start = False
            else:
                output_file.write(',\n')
            output_file.write('{"cell_type":"markdown","metadata":{},"source":"' + to_json(line)[1:-1])
            in_markdown = True
    if in_markdown:
        output_file.write('"}')
    elif in_code_block:
        output_file.write('","outputs":[]}')
    input_file.close()
    output_file.write('],\n"metadata":' + to_json(metadata) + '}')
    output_file.close()

def main():
    input_file_name = ''
    output_file_name = ''
    language = 'python'
    language_identifier = ''
    kernel = 'python3'
    encoding = 'UTF-8'
    overwrite = False
    argc = len(argv)
    k = argc - 1
    i = 1
    while i < argc:
        a = argv[i]
        if a in ('-h', '--help'):
            stdout.write(usage)
            exit()
        elif a in ('-e', '--encoding'):
            if i < k:
                encoding = argv[i+1]
                i += 2
                continue
            else:
                stderr.write("[Error] Expected an encoding after %s.\n" % a)
                exit(1)
        elif a in ('-o', '--output'):
            if i < k:
                output_file_name = argv[i+1]
                i += 2
                continue
            else:
                stderr.write("[Error] Expected a file name after %s.\n" % a)
                exit(1)
        elif a in ('-k', '--kernel'):
            if i < k:
                kernel = argv[i+1]
                i += 2
                continue
            else:
                stderr.write("[Error] Expected a name after %s.\n" % a)
                exit(1)
        elif a in ('-lang', '--language'):
            if i < k:
                language = argv[i+1]
                i += 2
                continue
            else:
                stderr.write("[Error] Expected a language name after %s.\n" % a)
                exit(1)
        elif a == '--language-identifier':
            if i < k:
                language_identifier = argv[i+1]
                i += 2
                continue
            else:
                stderr.write("[Error] Expected a language identifier after %s.\n" % a)
                exit(1)
        elif a == '--overwrite':
            overwrite = True
        else:
            input_file_name = a
        i += 1

    if input_file_name == '':
        stdout.write(usage)
        exit()
    elif output_file_name == '':
        if '.' in input_file_name:
            i = input_file_name.rindex('.')
            output_file_name = input_file_name[:i+1] + 'ipynb'
        else:
            output_file_name = input_file_name + '.ipynb'
    if exists(output_file_name) and not overwrite:
        stderr.write("[Error] '%s' exists. Use '--overwrite' to overwrite it.\n" % output_file_name)
        exit(2)
    if language_identifier == '':
        language_identifier = language

    convert(input_file_name, output_file_name, input_file_encoding=encoding, language=language, language_identifier=language_identifier, kernel=kernel)

if __name__ == '__main__':
    main()
