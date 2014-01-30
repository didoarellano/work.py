#!/usr/bin/env python

import os
import argparse
import subprocess


def main():
    parser = argparse.ArgumentParser(usage='work action [repository]')
    parser.add_argument('action', help='"start" or "end"')
    parser.add_argument('repository',
                        nargs='?',
                        default='all',
                        help='default is "all"')
    args = parser.parse_args()

    cwd = os.getcwd()
    if not in_git_toplevel(cwd):
        print('work needs to be called in a git-tracked project\'s root directory')
        return


def in_git_toplevel(dir):
    try:
        toplevel = subprocess.check_output(
            ['git', 'rev-parse', '--show-toplevel'],
            cwd=dir
        )
        return toplevel.strip() == dir
    except:
        return False


if __name__ == '__main__':
    main()
