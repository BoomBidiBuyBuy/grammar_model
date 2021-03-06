from model.model_fixtures import *
import pytest

@pytest.yield_fixture(scope="function")
def config(pool, nas, ntp):
    try:
        yield [nas, pool, SYSTEM]
    finally:
        pool().delete()
        ntp().delete()

def is_kerberos_existed(nas):
    return len([child for child in nas().children if child.name == KERBEROS.name and child.terminal]) > 0

def test_kerberos_create(config):
    nas = config[0]

    assert len(KERBEROS.list()) == 0
    assert not is_kerberos_existed(nas)

    kerberos = KERBEROS.create(nas)

    assert len(KERBEROS.list()) == 1
    assert kerberos().name == KERBEROS.name
    assert kerberos().terminal
    assert hasattr(kerberos(), 'id')
    assert kerberos().parent == nas()
    assert is_kerberos_existed(nas)

    KERBEROS.create(nas)

    assert len(KERBEROS.list()) == 1

    # tear down
    KERBEROS.delete(kerberos)

def test_kerberos_modify(config):
    nas = config[0]

    assert len(KERBEROS.list()) == 0
    assert not is_kerberos_existed(nas)

    kerberos = KERBEROS.create(nas)

    KERBEROS.modify(kerberos)

    assert is_kerberos_existed(nas)
    assert len(KERBEROS.list()) == 1
    assert kerberos().name == KERBEROS.name
    assert kerberos().terminal
    assert hasattr(kerberos(), 'id')
    assert kerberos().parent == nas()

    # tear down
    KERBEROS.delete(kerberos)

def test_kerberos_delete(config):
    nas1, pool, _ = config
    nas2 = NAS.create(pool)
    nas3 = NAS.create(pool)

    kerberos1 = KERBEROS.create(nas1)

    assert kerberos1().parent == nas1()
    assert is_kerberos_existed(nas1)
    assert not is_kerberos_existed(nas2)
    assert not is_kerberos_existed(nas3)
    assert len(KERBEROS.list()) == 1

    kerberos3 = KERBEROS.create(nas3)

    assert kerberos3().parent == nas3()
    assert is_kerberos_existed(nas1)
    assert not is_kerberos_existed(nas2)
    assert is_kerberos_existed(nas3)
    assert len(KERBEROS.list()) == 2

    kerberos2 = KERBEROS.create(nas2)

    assert kerberos2().parent == nas2()
    assert is_kerberos_existed(nas1)
    assert is_kerberos_existed(nas2)
    assert is_kerberos_existed(nas3)
    assert len(KERBEROS.list()) == 3

    KERBEROS.delete(kerberos1)

    assert kerberos1() == None
    assert not is_kerberos_existed(nas1)
    assert len(KERBEROS.list()) == 2

    kerberos1 = KERBEROS.create(nas1)

    assert kerberos1().parent == nas1()
    assert is_kerberos_existed(nas1)
    assert len(KERBEROS.list()) == 3

    KERBEROS.delete(kerberos1)
    KERBEROS.delete(kerberos2)
    KERBEROS.delete(kerberos3)

    assert kerberos1() == None
    assert kerberos2() == None
    assert kerberos3() == None
    assert len(KERBEROS.list()) == 0