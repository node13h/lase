# MIT license
# Copyright 2019 Sergej Alikov <sergej.alikov@gmail.com>

from lase import version


def test_next_dev_release():
    assert version.next_dev('1.2.3') == '1.2.4-SNAPSHOT'


def test_next_dev_snapshot():
    assert version.next_dev('1.2.3-SNAPSHOT') == '1.2.4-SNAPSHOT'


def test_next_dev_pre_num():
    assert version.next_dev('1.2.3-BETA1') == '1.2.3-BETA2-SNAPSHOT'


def test_next_dev_pre_num_snapshot():
    assert version.next_dev('1.2.3-BETA1-SNAPSHOT') == '1.2.3-BETA2-SNAPSHOT'


def test_next_dev_pre_num_only():
    assert version.next_dev('1.2.3-1') == '1.2.3-2-SNAPSHOT'


def test_next_dev_pre_num_oly_snapshot():
    assert version.next_dev('1.2.3-1-SNAPSHOT') == '1.2.3-2-SNAPSHOT'


def test_next_dev_pre():
    assert version.next_dev('1.2.3-BETA') == '1.2.4-SNAPSHOT'


def test_next_dev_pre_snapshot():
    assert version.next_dev('1.2.3-BETA-SNAPSHOT') == '1.2.4-SNAPSHOT'


def test_release_snapshot():
    assert version.release('1.2.3-SNAPSHOT') == '1.2.3'


def test_release_release():
    assert version.release('1.2.3') == '1.2.3'


def test_release_beta_snapshot():
    assert version.release('1.2.3-BETA1-SNAPSHOT') == '1.2.3-BETA1'


def test_release_beta_release():
    assert version.release('1.2.3-BETA1') == '1.2.3-BETA1'
