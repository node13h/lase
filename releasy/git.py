# MIT license
# Copyright 2019 Sergej Alikov <sergej.alikov@gmail.com>

from subprocess import run
import re
import logging

RE_LOCAL_BRANCH = r'^refs\/heads\/(.+)$'
RE_REMOTE_BRANCH = r'^refs\/remotes\/(.+?)\/(.+)$'


logger = logging.getLogger(__name__)


class NonZeroExitError(RuntimeError):
    pass


def cmd(params):
    logger.debug('Executing `{}`'.format(' '.join(params)))
    cp = run(params, capture_output=True, text=True)

    if cp.returncode != 0:
        for line in cp.stderr.strip('\n').splitlines():
            logger.debug('STDERR: {}'.format(line))

        raise NonZeroExitError('`{}` terminated with the non-zero exit code {}'.format(
            ' '.join(params), cp.returncode))

    return cp.stdout.strip('\n').splitlines()


def fetch(remote):
    cmd(['git', 'fetch', remote])


def checkout(branch):
    cmd(['git', 'checkout', branch])


def checkout_new_branch(branch):
    cmd(['git', 'checkout', '-b', branch])


def working_tree_is_clean(check_untracked_files=True):
    try:
        cmd(['git', 'diff-index', '--quiet', 'HEAD'])
    except NonZeroExitError:
        return False

    lines = cmd(['git', 'ls-files', '--exclude-standard', '--others'])

    if lines:
        for line in lines:
            logger.debug('Untracked file: {}'.format(line))

        return False

    return True


def branch_is_up_to_date(branch, remote):
    params = [
        'git',
        'rev-list',
        '{}..{}/{}'.format(branch, remote, branch),
        '--count']

    lines = cmd(params)

    if lines:
        try:
            symmetric_diff_count = int(lines[0])
        except ValueError:
            raise RuntimeError('`{}` returned non-numeric result {}'.format(
                ' '.join(params), lines[0]))
    else:
        raise RuntimeError('`{}` returned no output'.format(' '.join(params)))

    return symmetric_diff_count == 0


def branches_matching(regex, remote=None):
    result = set()

    params = [
        'git',
        'for-each-ref',
        '--format=%(refname)',
        'refs/heads']

    lines = cmd(params)

    pattern = re.compile(regex)

    for line in lines:
        match = re.match(RE_LOCAL_BRANCH, line)
        if match and pattern.match(match[1]):
            result.add(match[1])

    if remote is not None:
        params = [
            'git',
            'for-each-ref',
            '--format=%(refname)',
            'refs/remotes/{}'.format(remote)]

        lines = cmd(params)

        for line in lines:
            match = re.match(RE_REMOTE_BRANCH, line)
            if match and match[1] == remote and pattern.match(match[2]):
                result.add(match[2])

    return result


def staged_files():
    return cmd(['git', 'diff', '--name-only', '--cached'])


def commit(files, message):
    cmd(['git', 'add'] + list(files))

    if staged_files():
        cmd(['git', 'commit', '-m', message])


def push(remote, branch):
    cmd(['git', 'push', remote, branch])


def merge(branch, message, remote=None):
    if remote is None:
        params = ['git', 'merge', branch]
    else:
        params = ['git', 'merge', '{}/{}'.format(remote, branch)]

    cmd(params)


def tag(tagname, message):
    cmd(['git', 'tag', '-a', tagname, '-m', message])


def user_name():
    try:
        lines = cmd(['git', 'config', 'user.name'])
    except NonZeroExitError:
        return None

    if lines:
        return lines[0]
    else:
        return None


def delete_branch(branch, remote=None):
    if remote is not None:
        cmd(['git', 'push', remote, '--delete', branch])

    cmd(['git', 'branch', '-d', branch])
