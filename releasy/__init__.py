# MIT license
# Copyright 2019 Sergej Alikov <sergej.alikov@gmail.com>

from . import version
from . import git


def start(release_version=None, remote=None, version_file='VERSION'):
    if not git.working_tree_is_clean():
        raise RuntimeError('Working tree is not clean')

    if remote is not None:
        git.fetch(remote)

    release_branches = git.branches_matching(r'^release/.*', remote=remote)

    if release_branches:
        raise RuntimeError('Existing release branch(es) ({}) found'.format(
            ', '.join(release_branches)))

    if remote is not None and not git.branch_is_up_to_date('develop'):
        raise RuntimeError('develop branch is not up to date')

    # Begin mutation

    git.checkout('develop')

    if release_version is None:
        current_version = version.from_file(version_file)
        release_version = version.release(current_version)

    next_version = version.next_dev(release_version)
    release_branch = 'release/{}'.format(release_version)

    version.to_file(next_version, version_file)

    git.commit((version_file,), 'Start {}'.format(next_version))

    if remote is not None:
        git.push(remote, 'develop')

    git.checkout_new_branch(release_branch)

    version.to_file(release_version, version_file)

    git.commit((version_file,), 'Release start {}'.format(release_version))

    if remote is not None:
        git.push(remote, release_branch)


def finish(remote=None, version_file='VERSION'):
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

    if remote is not None:
        for branch in ('develop', 'master', release_branch):
            if not git.branch_is_up_to_date(branch):
                raise RuntimeError('{} branch is not up to date'.format(branch))

    user_name = git.user_name()

    # Begin mutation

    git.checkout('master')

    git.merge(release_branch, 'Merge {}'.format(release_branch), remote=remote)

    if remote is not None:
        git.push(remote, 'master')

    release_version = version.from_file(version_file)

    if user_name is not None:
        release_message = 'Release {} by {}'.format(release_version, user_name)
    else:
        release_message = 'Release {}'.format(release_version)

    git.tag(release_version, release_message)

    if remote is not None:
        git.push(remote, release_version)

    git.checkout('develop')

    current_version = version.from_file(version_file)

    git.merge('master', 'Merge master', remote=remote)

    version.to_file(current_version, version_file)

    git.commit((version_file,), 'Restore the current version {}'.format(current_version))

    if remote is not None:
        git.push(remote, 'develop')

    git.delete_branch(release_branch, remote=remote)
