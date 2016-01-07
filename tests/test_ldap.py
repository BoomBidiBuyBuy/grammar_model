from model.model_fixtures import *
import pytest

@pytest.yield_fixture(scope="function")
def config(nas, pool):
    try:
        yield [nas, pool, SYSTEM]
    finally:
        pool().delete()

def is_ldap_existed(nas):
    return len([child for child in nas().children if child.name == LDAP.name and child.terminal]) > 0

def test_ldap_create(config):
    nas = config[0]

    assert len(LDAP.list()) == 0
    assert not is_ldap_existed(nas)

    LDAP.create(nas)

    # don't create LDAP, because there is no Interface
    assert len(LDAP.list()) == 0

    fi = FI.create(nas)

    ldap = LDAP.create(nas)

    assert len(LDAP.list()) == 1
    assert ldap().parent == nas()
    assert ldap().name == LDAP.name
    assert ldap().terminal
    assert hasattr(ldap(), 'id')
    assert is_ldap_existed(nas)

    # tear down
    FI.delete(fi)
    LDAP.delete(ldap)

def test_ldap_modify(config):
    nas = config[0]

    assert len(LDAP.list()) == 0
    assert not is_ldap_existed(nas)

    fi = FI.create(nas)
    ldap = LDAP.create(nas)

    assert is_ldap_existed(nas)
    assert len(LDAP.list()) == 1
    assert ldap().name == LDAP.name
    assert ldap().terminal == True
    assert hasattr(ldap(), 'id')
    assert ldap().parent == nas()

    # tear down
    FI.delete(fi)
    LDAP.delete(ldap)

def test_ldap_delete(config):
    nas1, pool, _ = config
    nas2 = NAS.create(pool)
    nas3 = NAS.create(pool)

    fi1, fi2, fi3 = FI.create(nas1), FI.create(nas2), FI.create(nas3)

    ldap1 = LDAP.create(nas1)

    assert ldap1().parent == nas1()
    assert is_ldap_existed(nas1)
    assert not is_ldap_existed(nas2)
    assert not is_ldap_existed(nas3)
    assert len(LDAP.list()) == 1

    ldap3 = LDAP.create(nas3)

    assert ldap3().parent == nas3()
    assert is_ldap_existed(nas1)
    assert not is_ldap_existed(nas2)
    assert is_ldap_existed(nas3)
    assert len(LDAP.list()) == 2

    ldap2 = LDAP.create(nas2)

    assert ldap2().parent == nas2()
    assert is_ldap_existed(nas1)
    assert is_ldap_existed(nas2)
    assert is_ldap_existed(nas3)
    assert len(LDAP.list()) == 3

    LDAP.delete(ldap2)

    assert ldap2() == None
    assert not is_ldap_existed(nas2)
    assert len(LDAP.list()) == 2

    LDAP.delete(ldap1)

    assert ldap1() == None
    assert not is_ldap_existed(nas1)
    assert len(LDAP.list()) == 1

    LDAP.delete(ldap3)

    assert ldap3() == None
    assert not is_ldap_existed(nas3)
    assert len(LDAP.list()) == 0

    ldap2 = LDAP.create(nas2)

    assert ldap2().parent == nas2()
    assert is_ldap_existed(nas2)
    assert len(LDAP.list()) == 1

    LDAP.delete(ldap2)

    assert len(LDAP.list()) == 0

    # tear down
    FI.delete(fi1)
    FI.delete(fi2)
    FI.delete(fi3)

