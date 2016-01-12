from model.model_fixtures import *
import pytest

@pytest.yield_fixture(scope="function")
def config(pool, nas):
    try:
        yield [nas, pool, SYSTEM]
    finally:
        while len(POOL.list()):
            POOL.delete(POOL.list()[0])

        while len(NTP.list()):
            NTP.delete(NTP.list()[0])

def is_cifs_existed(nas):
    return len([child for child in nas().children if child.name == CIFS.name and child.terminal]) > 0

def test_cifs_create(config):
    nas, pool, system = config

    assert len(CIFS_J.list()) == 0
    assert not is_cifs_existed(nas)

    CIFS_J.create(nas)
    # nothing, because there are no created dependencies
    assert len(CIFS_J.list()) == 0

    ntp = NTP.create(system)
    assert ntp().parent == system

    CIFS_J.create(nas)
    # nothing, because only NTP isn't enough
    assert len(CIFS_J.list()) == 0

    fi = FI.create(nas)
    assert fi().parent.parent == nas()

    CIFS_J.create(nas)
    # nothing, because DNS is required too
    assert len(CIFS_J.list()) == 0

    dns = DNS.create(nas)
    assert dns().parent == nas()

    cifs = CIFS_J.create(nas)
    assert len(CIFS.list()) == 1
    assert len(CIFS_J.list()) == 1
    assert cifs().name == CIFS.name
    assert cifs().terminal
    assert hasattr(cifs(), 'id')
    assert cifs().parent == nas()
    assert is_cifs_existed(nas)

def test_cifs_modify(config):
    nas, pool, system = config

    assert not is_cifs_existed(nas)

    NTP.create(system)
    FI.create(nas)
    DNS.create(nas)
    cifs = CIFS_J.create(nas)

    CIFS_J.modify(cifs)

    assert is_cifs_existed(nas)
    assert cifs().name == CIFS.name
    assert cifs().terminal
    assert hasattr(cifs(), 'id')
    assert cifs().parent == nas()

def test_cifs_delete(config):
    nas1, pool, system = config
    nas2, nas3 = NAS.create(pool), NAS.create(pool)
    nases = [nas1, nas2, nas3]

    for nas in nases:
        assert not is_cifs_existed(nas)

    NTP.create(system)
    [FI.create(nas) for nas in nases]
    [DNS.create(nas) for nas in nases]

    cifs1 = CIFS_J.create(nas1)
    assert cifs1().parent == nas1()
    assert is_cifs_existed(nas1)
    assert not is_cifs_existed(nas2)
    assert not is_cifs_existed(nas3)
    assert len(CIFS_J.list()) == 1

    cifs3 = CIFS_J.create(nas3)
    assert cifs3().parent == nas3()
    assert is_cifs_existed(nas1)
    assert not is_cifs_existed(nas2)
    assert is_cifs_existed(nas3)
    assert len(CIFS_J.list()) == 2

    cifs2 = CIFS_J.create(nas2)
    assert cifs2().parent == nas2()
    assert is_cifs_existed(nas1)
    assert is_cifs_existed(nas2)
    assert is_cifs_existed(nas3)
    assert len(CIFS_J.list()) == 3

    # valid deletions check
    CIFS_J.delete(cifs1)
    assert cifs1() == None
    assert not is_cifs_existed(nas1)
    assert len(CIFS_J.list()) == 2

    cifs1 = CIFS_J.create(nas1)
    assert cifs1().parent == nas1()
    assert len(CIFS_J.list()) == 3

    CIFS_J.delete(cifs2)
    assert cifs2() == None
    assert len(CIFS_J.list()) == 2

    CIFS_J.delete(cifs3)
    assert cifs3() == None
    assert len(CIFS_J.list()) == 1

    CIFS_J.delete(cifs1)
    assert cifs1() == None
    assert len(CIFS_J.list()) == 0

def test_cifs_delete_deps(config):
    nas, pool, system = config

    ntp = NTP.create(system)
    fi = FI.create(nas)
    dns = DNS.create(nas)

    cifs = CIFS_J.create(nas)
    assert len(CIFS_J.list()) == 1
    assert cifs().parent == nas()

    #----------------#
    # try to delete without interface
    FI.delete(fi)

    CIFS_J.delete(cifs)
    assert len(CIFS_J.list()) == 1

    FI.create(nas)

    #----------------#
    # try to delete without dns
    DNS.delete(dns)

    CIFS_J.delete(cifs)
    assert len(CIFS_J.list()) == 1

    DNS.create(nas)

    #----------------#
    # try to delete without NTP

    NTP.delete(ntp)

    CIFS_J.delete(cifs)
    assert len(CIFS_J.list()) == 1

    NTP.create(system)

def test_cifs_diff_pools(config):
    nas, pool1, system = config
    pool2 = POOL.create(system)

    p1n1, p1n2 = nas, NAS.create(pool1)
    p2n1, p2n2 = NAS.create(pool2), NAS.create(pool2)

    nases = [p1n1, p1n2, p2n1, p2n2]

    NTP.create(system)
    [FI.create(nas) for nas in nases]
    [DNS.create(dns) for dns in nases]

    #----------------#
    cifs1 = CIFS_J.create(p1n2)
    cifs2 = CIFS_J.create(p2n2)

    assert len(CIFS_J.list()) == 2
    assert is_cifs_existed(p1n2)
    assert is_cifs_existed(p2n2)

    #----------------#
    CIFS_J.delete(cifs2)

    assert len(CIFS_J.list()) == 1
    assert cifs2() is None
    assert not is_cifs_existed(p2n2)

    #----------------#
    cifs2 = CIFS_J.create(p2n1)

    assert is_cifs_existed(p2n1)
    assert len(CIFS_J.list()) == 2

    #----------------#
    POOL.delete(pool1)

    assert len(CIFS_J.list()) == 1
    assert cifs1() is None
    assert not cifs2() is None

    #----------------#
    NAS.delete(p2n2)

    assert len(CIFS_J.list()) == 1
    assert cifs1() is None
    assert not cifs2() is None

    #----------------#
    NAS.delete(p2n1)

    assert len(CIFS_J.list()) == 0
    assert cifs1() is None
    assert cifs2() is None

def test_cifs_both_deletion(config):
    nas1, pool, system = config
    nas2 = NAS.create(pool)
    FI.create(nas2)
    DNS.create(nas2)
    NTP.create(system)

    cifs_sa = CIFS_SA.create(nas1)
    cifs_j = CIFS_J.create(nas2)
    assert not cifs_sa() is None
    assert not cifs_j() is None
    assert len(CIFS.list()) == 2
    assert len(CIFS_SA.list()) == 1
    assert len(CIFS_J.list()) == 1

    for cifs in CIFS.list():
        cifs().delete()

    assert cifs_sa() is None
    assert cifs_j() is None
    assert len(CIFS.list()) == 0
    assert len(CIFS_SA.list()) == 0
    assert len(CIFS_J.list()) == 0