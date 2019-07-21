#!/usr/bin/env bash

# MIT license
# Copyright 2019 Sergej Alikov <sergej.alikov@gmail.com>

__DOC__='Functional tests for Lase'

set -euo pipefail

# shellcheck disable=SC1091
source shelter.sh


TEMP_DIR=$(mktemp -d)

_cleanup () {
    rm -rf -- "${TEMP_DIR}/test_"*

    rmdir "$TEMP_DIR"

    if [[ "${#SAVED_EXIT_TRAP_CMD[@]}" -gt 0 ]]; then
        eval "${SAVED_EXIT_TRAP_CMD[2]}"
    fi
}

eval "declare -a SAVED_EXIT_TRAP_CMD=($(trap -p EXIT))"
trap _cleanup EXIT


test_local_next_release () {
    declare workspace="${TEMP_DIR}/${FUNCNAME[0]}"

    mkdir -p "${workspace}/local"

    cd "${workspace}/local"
    git init .

    touch foo
    git add foo
    git commit -m 'Add foo'
    git checkout -b develop
    printf '0.1.0-SNAPSHOT\n' >VERSION
    git add VERSION
    git commit -m 'Add VERSION'

    lase start

    assert_stdout 'cat VERSION' <<< '0.1.0'
    assert_stdout 'git rev-parse --abbrev-ref HEAD' <<< 'release/0.1.0'

    lase finish

    assert_stdout 'git rev-parse --abbrev-ref HEAD' <<< 'develop'

    assert_stdout 'cat VERSION' <<< '0.1.1-SNAPSHOT'
    assert_stdout_not_contains 'git for-each-ref --format="%(refname)" refs/heads' '^refs/heads/release/'

    assert_stdout_contains 'git for-each-ref --format="%(refname)" refs/tags' '^refs/tags/0.1.0$'

    git checkout master

    assert_stdout 'cat VERSION' <<< '0.1.0'
}


test_local_specific_release () {
    declare workspace="${TEMP_DIR}/${FUNCNAME[0]}"

    mkdir -p "${workspace}/local"

    cd "${workspace}/local"
    git init .

    touch foo
    git add foo
    git commit -m 'Add foo'
    git checkout -b develop
    printf '0.1.0-SNAPSHOT\n' >VERSION
    git add VERSION
    git commit -m 'Add VERSION'

    lase start --version '1.2.3'

    assert_stdout 'cat VERSION' <<< '1.2.3'
    assert_stdout 'git rev-parse --abbrev-ref HEAD' <<< 'release/1.2.3'

    lase finish

    assert_stdout 'git rev-parse --abbrev-ref HEAD' <<< 'develop'

    assert_stdout 'cat VERSION' <<< '1.2.4-SNAPSHOT'
    assert_stdout_not_contains 'git for-each-ref --format="%(refname)" refs/heads' '^refs/heads/release/'

    assert_stdout_contains 'git for-each-ref --format="%(refname)" refs/tags' '^refs/tags/1.2.3$'

    git checkout master

    assert_stdout 'cat VERSION' <<< '1.2.3'
}


test_local_next_pre_release () {
    declare workspace="${TEMP_DIR}/${FUNCNAME[0]}"

    mkdir -p "${workspace}/local"

    cd "${workspace}/local"
    git init .

    touch foo
    git add foo
    git commit -m 'Add foo'
    git checkout -b develop
    printf '0.1.0-BETA2-SNAPSHOT\n' >VERSION
    git add VERSION
    git commit -m 'Add VERSION'

    lase start

    assert_stdout 'cat VERSION' <<< '0.1.0-BETA2'
    assert_stdout 'git rev-parse --abbrev-ref HEAD' <<< 'release/0.1.0-BETA2'

    lase finish

    assert_stdout 'git rev-parse --abbrev-ref HEAD' <<< 'develop'

    assert_stdout 'cat VERSION' <<< '0.1.0-BETA3-SNAPSHOT'
    assert_stdout_not_contains 'git for-each-ref --format="%(refname)" refs/heads' '^refs/heads/release/'

    assert_stdout_contains 'git for-each-ref --format="%(refname)" refs/tags' '^refs/tags/0.1.0-BETA2$'

    git checkout master

    assert_stdout 'cat VERSION' <<< '0.1.0-BETA2'
}


test_local_fails_on_existing_release () {
    declare workspace="${TEMP_DIR}/${FUNCNAME[0]}"

    mkdir -p "${workspace}/local"

    cd "${workspace}/local"
    git init .

    touch foo
    git add foo
    git commit -m 'Add foo'
    git checkout -b develop
    printf '0.1.0-SNAPSHOT\n' >VERSION
    git add VERSION
    git commit -m 'Add VERSION'

    lase start

    assert_fail 'lase start'
}


test_with_remote_next_release () {
    declare workspace="${TEMP_DIR}/${FUNCNAME[0]}"

    mkdir -p "${workspace}/remote"

    cd "${workspace}/remote"
    git init --bare .

    mkdir -p "${workspace}/checkout1"
    cd "${workspace}/checkout1"

    git clone "${workspace}/remote" .

    touch foo
    git add foo
    git commit -m 'Add foo'
    git checkout -b develop
    printf '0.1.0-SNAPSHOT\n' >VERSION
    git add VERSION
    git commit -m 'Add VERSION'
    git push origin master
    git push origin develop

    mkdir -p "${workspace}/checkout2"
    cd "${workspace}/checkout2"

    git clone "${workspace}/remote" .

    lase --remote origin start

    assert_stdout 'cat VERSION' <<< '0.1.0'
    assert_stdout 'git rev-parse --abbrev-ref HEAD' <<< 'release/0.1.0'

    lase --remote origin finish

    assert_stdout 'git rev-parse --abbrev-ref HEAD' <<< 'develop'

    assert_stdout 'cat VERSION' <<< '0.1.1-SNAPSHOT'
    assert_stdout_not_contains 'git for-each-ref --format="%(refname)" refs/heads' '^refs/heads/release/'
    assert_stdout_not_contains 'git for-each-ref --format="%(refname)" refs/remotes' '^refs/remotes/origin/release/'

    assert_stdout_contains 'git for-each-ref --format="%(refname)" refs/tags' '^refs/tags/0.1.0$'

    git checkout master

    assert_stdout 'cat VERSION' <<< '0.1.0'
}


test_with_remote_fails_on_existing_release () {
    declare workspace="${TEMP_DIR}/${FUNCNAME[0]}"

    mkdir -p "${workspace}/remote"

    cd "${workspace}/remote"
    git init --bare .

    mkdir -p "${workspace}/checkout1"
    cd "${workspace}/checkout1"

    git clone "${workspace}/remote" .

    touch foo
    git add foo
    git commit -m 'Add foo'
    git checkout -b develop
    printf '0.1.0-SNAPSHOT\n' >VERSION
    git add VERSION
    git commit -m 'Add VERSION'
    git push origin master
    git push origin develop

    lase --remote origin start

    mkdir -p "${workspace}/checkout2"
    cd "${workspace}/checkout2"

    git clone "${workspace}/remote" .

    assert_fail 'lase --remote origin start'
}


suite () {
    shelter_run_test_class Local test_local_
    shelter_run_test_class Remote test_with_remote_
}

usage () {
    cat <<EOF
Usage: ${0} [--help]
${__DOC__}

ENVIRONMENT VARIABLES:
  ENABLE_CI_MODE    set to non-empty value to enable the Junit XML
                    output mode

EOF
}

main () {
    if [[ "${1:-}" = '--help' ]]; then
        usage
        return 0
    fi

    supported_shelter_versions 0.7

    if [[ -n "${ENABLE_CI_MODE:-}" ]]; then
        mkdir -p junit
        shelter_run_test_suite suite | shelter_junit_formatter >junit/test_libautomated.xml
    else
        shelter_run_test_suite suite | shelter_human_formatter
    fi
}


if ! (return 2>/dev/null); then
    main "$@"
fi
