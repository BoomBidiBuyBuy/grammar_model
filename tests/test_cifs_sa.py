from model.model_fixtures import *
import pytest

@pytest.yield_fixture(scope="function")
def config(pool_type, nas_type, fi_type, dns_type, ntp_type, cifs_j_type, cifs_sa_type):
    [globals().update(obj) for obj in [pool_type, nas_type, fi_type, dns_type, ntp_type, cifs_j_type, cifs_sa_type]]

    system_node = Node(name="*", terminal=False)
    system_node.add(Node(POOL.name, terminal=False))
    system_node.add(Node(NTP.name, terminal=False))

    pool = POOL.create(system_node)
    nas = NAS.create(pool)

    try:
        yield [nas, pool, system_node]
    finally:
        while len(NTP.list()):
            NTP.delete(NTP.list()[0])

        while len(POOL.list()):
            POOL.delete(POOL.list()[0])

def is_cifs_existed(nas):
    return len([child for child in nas().children if child.name == 'CIFS' and not child.terminal]) == 0

def is_cifs_j_existed(nas):
    return len([child for child in nas().children if child.name == CIFS_J.name and child.terminal]) > 0

def is_cifs_sa_existed(nas):
    return len([child for child in nas().children if child.name == CIFS_SA.name and child.terminal]) > 0

def test_cifs_sa_create(config):
    nas, pool, system = config

    assert len(CIFS_SA.list()) == 0
    assert not is_cifs_existed(nas)

    cifs = CIFS_SA.create(nas)

    assert len(CIFS_SA.list()) == 1
    assert cifs().name == CIFS_SA.name
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
    assert cifs().name == CIFS_SA.name
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

