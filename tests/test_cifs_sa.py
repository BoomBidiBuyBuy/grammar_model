from model.model_fixtures import *
import pytest

@pytest.yield_fixture(scope="function")
def config(pool, nas):
    try:
        yield [nas, pool, SYSTEM]
    finally:
        pool().delete()

        while len(NTP.list()):
            NTP.delete(NTP.list()[0])

def is_cifs_existed(nas):
    return len([child for child in nas().children if child.name == CIFS.name and not child.terminal]) == 0

def is_cifs_j_existed(nas):
    return len([child for child in nas().children if child.type == CIFS_J.name and child.terminal]) > 0

def is_cifs_sa_existed(nas):
    return len([child for child in nas().children if child.type == CIFS_SA.name and child.terminal]) > 0

def test_cifs_sa_create(config):
    nas, pool, system = config

    assert len(CIFS_SA.list()) == 0
    assert not is_cifs_existed(nas)

    cifs = CIFS_SA.create(nas)

    assert len(CIFS_SA.list()) == 1
    assert len(CIFS.list()) == 1
    assert cifs().name == CIFS.name
    assert cifs().terminal
    assert hasattr(cifs(), 'id')
    assert cifs().parent == nas()
    assert is_cifs_existed(nas)

    CIFS_SA.create(nas)

    assert len(CIFS_SA.list()) == 1

def test_cifs_sa_modify(config):
    nas, pool, system = config

    assert not is_cifs_existed(nas)

    cifs = CIFS_SA.create(nas)

    CIFS_SA.modify(cifs)

    assert is_cifs_existed(nas)
    assert len(CIFS_SA.list()) == 1
    assert cifs().name == CIFS.name
    assert cifs().type == CIFS_SA.name
    assert cifs().terminal
    assert hasattr(cifs(), 'id')
    assert cifs().parent == nas()

def test_cifs_sa_and_j(config):
    nas, pool, system = config

    assert not is_cifs_existed(nas)

    FI.create(nas)
    DNS.create(nas)
    NTP.create(system)

    cifs = CIFS_SA.create(nas)

    assert not cifs() is None
    assert CIFS_J.create(nas) is None
    assert is_cifs_existed(nas)
    assert is_cifs_sa_existed(nas)
    assert not is_cifs_j_existed(nas)

    CIFS_SA.delete(nas)

    assert cifs() is None
    assert not is_cifs_existed(nas)
    assert not is_cifs_sa_existed(nas)
    assert not is_cifs_j_existed(nas)

    cifs = CIFS_J.create(nas)

    assert not cifs() is None
    assert CIFS_SA.create(nas) is None
    assert is_cifs_existed(nas)
    assert not is_cifs_sa_existed(nas)
    assert is_cifs_j_existed(nas)

