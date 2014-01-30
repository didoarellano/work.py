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

    if args.action == 'start':
        revert_repository_state(cwd)
    elif args.repository != 'all':
        save_repository_state(cwd)


def in_git_toplevel(dir):
    try:
        toplevel = subprocess.check_output(
            ['git', 'rev-parse', '--show-toplevel'],
            cwd=dir
        )
        return toplevel.strip() == dir
    except:
        return False


def save_repository_state(dir):
    commit_message = 'Work end checkpoint commit'
    subprocess.call(['git', 'checkout', '-B', 'work-end-checkpoint'], cwd=dir)
    subprocess.call(['git', 'add', '.'], cwd=dir)
    subprocess.call(['git', 'commit', '--message', commit_message], cwd=dir)


def revert_repository_state(dir):
    try:
        subprocess.check_call(['git', 'checkout', 'work-end-checkpoint'], cwd=dir)
    except subprocess.CalledProcessError:
        print('No work-end-checkpoint branch found.')
    else:
        master_tip_sha = subprocess.check_output(['git', 'rev-parse', 'master'],
                                                 cwd=dir).strip()
        subprocess.call(['git', 'reset', master_tip_sha], cwd=dir)
        subprocess.call(['git', 'checkout', 'master'], cwd=dir)


if __name__ == '__main__':
    main()
