#!/usr/bin/env python

import os
import argparse
import subprocess


TMPFILE = os.path.join(os.environ['HOME'], '.work-worked-on')


def main():
    args = define_arguments().parse_args()
    cwd = os.getcwd()

    if not in_git_toplevel(cwd):
        print('work needs to be called in a git-tracked project\'s root directory')
        return

    if args.action == 'start':
        print('\nStarting work on project: {0}'.format(os.path.basename(cwd)))
        revert_repository_state(cwd)
        add_repo_to_tmpfile(cwd, TMPFILE)
        show_git_status(cwd)

    else:
        repo_arg = args.repository
        if repo_arg == '.':
            repos = [cwd]
        elif os.path.isdir(repo_arg) and in_git_toplevel(repo_arg):
            repos = [repo_arg]
        else:
            repos = get_worked_on(TMPFILE)

        for repo in repos:
            print('\nEnding work on project: {0}'.format(os.path.basename(repo)))
            save_repository_state(repo)
            push_to_remote(repo, remote=args.remote, force=True)
            remove_repo_from_tmpfile(repo, TMPFILE)


def define_arguments():
    parser = argparse.ArgumentParser(usage='work action [repository]')
    parser.add_argument('action', help='"start" or "end"')
    parser.add_argument('repository',
                        nargs='?',
                        default='all',
                        help='default is "all"')
    parser.add_argument('-r', '--remote',
                        default='private',
                        help='Git remote to push to. Default is "private"')
    return parser


def show_git_status(repo):
    print('')
    subprocess.call(['git', 'status'])


def remote_exists(repo, remote):
    remotes = subprocess.check_output(['git', 'remote'], cwd=repo)
    return remote in remotes


def branch_exists(repo, branch):
    branches = subprocess.check_output(['git', 'branch'], cwd=repo)
    return branch in branches


def push_to_remote(repo, remote='origin', force=False):
    if not remote_exists(repo, remote):
        print('\nThe remote "{0}" doesn\'t exist. Cancelling `git push`.'.format(remote))
    else:
        print('\nPushing work-end-checkpoint to {0} remote.'.format(remote))
        command = ['git', 'push', remote, '+work-end-checkpoint']
        force and command.append('--force')
        subprocess.call(command, cwd=repo)


def in_git_toplevel(dir):
    try:
        toplevel = subprocess.check_output(
            ['git', 'rev-parse', '--show-toplevel'],
            cwd=dir
        )
        return toplevel.strip() == dir
    except:
        return False


def save_repository_state(repo):
    print('\nCommiting working tree to work-end-checkpoint branch.')
    commit_message = 'Work end checkpoint commit'
    subprocess.call(['git', 'checkout', '-B', 'work-end-checkpoint'], cwd=repo)
    subprocess.call(['git', 'add', '.'], cwd=repo)
    subprocess.call(['git', 'commit', '--message', commit_message], cwd=repo)


def revert_repository_state(repo):
    if not branch_exists(repo, 'work-end-checkpoint'):
        print('\nNo work-end-checkpoint branch found. Cancelling reset to master.')
    else:
        print('\nResetting to tip of master branch and deleting the work-end-checkpoint branch.')
        master_tip_sha = subprocess.check_output(['git', 'rev-parse', 'master'],
                                                 cwd=repo).strip()
        subprocess.call(['git', 'checkout', 'work-end-checkpoint'], cwd=repo)
        subprocess.call(['git', 'reset', master_tip_sha], cwd=repo)
        subprocess.call(['git', 'checkout', 'master'], cwd=repo)
        subprocess.call(['git', 'branch', '--delete', 'work-end-checkpoint'], cwd=repo)


def add_repo_to_tmpfile(repo, tmpfile):
    with open(tmpfile, 'a+') as f:
        if repo in [line.strip() for line in f.readlines()]:
            print('\n{0} already in temp file.'.format(repo))
        else:
            print('\nAdding {0} to temp file.'.format(repo))
            f.write(repo + '\n')


def remove_repo_from_tmpfile(repo, tmpfile):
    with open(tmpfile, 'r+') as f:
        keep = [line for line in f.readlines() if repo != line.strip()]
        print('\nRemoving {0} from temp file.'.format(repo))
        f.seek(0)
        f.writelines(keep)
        f.truncate()


def get_worked_on(tmpfile):
    with open(tmpfile, 'r') as f:
        return [repo.strip() for repo in f.readlines()]


if __name__ == '__main__':
    main()
