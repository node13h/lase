# MIT license
# Copyright 2019 Sergej Alikov <sergej.alikov@gmail.com>

import sys
import argparse
import logging
import json

from . import version
from . import git

logger = logging.getLogger(__name__)


def start(
        release_version=None, version_file='VERSION', remote=None,
        develop_branch='develop'):

    if not git.working_tree_is_clean():
        raise RuntimeError('Working tree is not clean')

    if remote is not None:
        git.fetch(remote)

    release_branches = git.branches_matching(r'^release/.*', remote=remote)

    if release_branches:
        raise RuntimeError('Existing release branch(es) ({}) found'.format(
            ', '.join(release_branches)))

    # Begin mutation

    git.checkout(develop_branch)

    if remote is not None and not git.branch_is_up_to_date(develop_branch, remote):
        raise RuntimeError('{} branch is not up to date'.format(develop_branch))

    if release_version is None:
        current_version = version.from_file(version_file)
        release_version = version.release(current_version)

    next_version = version.next_dev(release_version)
    release_branch = 'release/{}'.format(release_version)

    version.to_file(next_version, version_file)

    git.commit((version_file,), 'Start {}'.format(next_version))

    if remote is not None:
        git.push(remote, develop_branch)

    git.checkout_new_branch(release_branch)

    version.to_file(release_version, version_file)

    git.commit((version_file,), 'Release start {}'.format(release_version))

    if remote is not None:
        git.push(remote, release_branch)

    return {
        'release_version': release_version,
        'release_branch': release_branch,
        'next_version': next_version,
    }


def finish(
        version_file='VERSION', remote=None,
        develop_branch='develop', master_branch='master'):

    if not git.working_tree_is_clean():
        raise RuntimeError('Working tree is not clean')

    if remote is not None:
        git.fetch(remote)

    release_branches = git.branches_matching(r'^release/.*', remote=remote)

    if len(release_branches) > 1:
        raise RuntimeError('More than one release branch ({}) found'.format(
            ', '.join(release_branches)))

    if len(release_branches) < 1:
        raise RuntimeError('No release branches found')

    release_branch = list(release_branches)[0]

    user_name = git.user_name()

    # Begin mutation

    # Abort early if any of the branches are not up-to-date
    if remote is not None:
        for branch in filter(None, (develop_branch, master_branch, release_branch)):
            git.checkout(branch)
            if not git.branch_is_up_to_date(branch, remote):
                raise RuntimeError('{} branch is not up to date'.format(branch))

    if master_branch:
        git.checkout(master_branch)

        git.merge(release_branch, 'Merge {}'.format(release_branch), remote=remote)

        if remote is not None:
            git.push(remote, master_branch)
    else:
        git.checkout(release_branch)

    release_version = version.from_file(version_file)

    if user_name is not None:
        release_message = 'Release {} by {}'.format(release_version, user_name)
    else:
        release_message = 'Release {}'.format(release_version)

    release_tag = release_version

    git.tag(release_tag, release_message)

    if remote is not None:
        git.push(remote, release_tag)

    git.checkout(develop_branch)

    current_version = version.from_file(version_file)

    if master_branch:
        git.merge(master_branch, 'Merge {}'.format(master_branch), remote=remote)
    else:
        git.merge(release_branch, 'Merge {}'.format(release_branch), remote=remote)

    version.to_file(current_version, version_file)

    git.commit((version_file,), 'Restore the current version {}'.format(current_version))

    if remote is not None:
        git.push(remote, develop_branch)

    git.delete_branch(release_branch, remote=remote)

    git.checkout(release_tag)

    return {
        'release_version': release_version,
        'release_tag': release_tag
    }


def parse_args(argv):
    parser = argparse.ArgumentParser(
        description='Gitflow release tool',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument(
        '--debug', action='store_true', default=False,
        help='enable debug output')

    parser.add_argument(
        '--remote',
        help='remote name to work with. Leave unset for local-only operation')

    parser.add_argument(
        '--master-branch',
        default='master',
        help='name of the master branch')

    parser.add_argument(
        '--skip-master', action='store_true', default=False,
        help='do not involve master branch')

    parser.add_argument(
        '--develop-branch',
        default='develop',
        help='name of the develop branch')

    parser.add_argument(
        '--json', action='store_true', default=False,
        help='enable JSON output')

    parser.add_argument(
        '--version-file',
        default='VERSION',
        help='version file name')

    commands = parser.add_subparsers(title='commands', dest='command')

    start_parser = commands.add_parser('start')

    start_parser.add_argument(
        '--version',
        help='the version to release. Will be computed if not specified')

    commands.add_parser('finish')

    return parser.parse_args()


def main():
    args = parse_args(sys.argv[1:])

    if args.debug:
        log_level = logging.DEBUG
    else:
        log_level = logging.WARN

    logging.basicConfig(level=log_level)

    try:
        if args.skip_master:
            master_branch = None
        else:
            master_branch = args.master_branch

        if args.command == 'start':
            result = start(
                args.version, args.version_file, args.remote, args.develop_branch)
        elif args.command == 'finish':
            result = finish(
                args.version_file, args.remote, args.develop_branch, master_branch)

        if args.json:
            print(json.dumps(result))
    except Exception as e:
        logger.error(str(e))

        if args.debug:
            raise
        else:
            return 1

    return 0
