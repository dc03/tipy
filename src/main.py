import sys
from typing import *

from Error import *
from Executor import Executor
from Parser import Parser
from Scanner import Scanner


def main():
    if len(sys.argv) != 2:
        error('Need only file name')

    file_name = sys.argv[1]

    if not file_name.endswith('.ti'):
        error('File extension not recognized')

    file = open(file_name, 'rt')

    if not file:
        error('Unable to open file')

    scanner = Scanner()
    tokens = scanner.scan(file)
    parser = Parser()
    parser.parse(tokens)
    executor = Executor()
    return executor.execute(parser.parse(tokens))


if __name__ == '__main__':
    exit(main())
