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

def is_nfs_existed(nas):
    return len([child for child in nas().children if child.terminal and child.name == NFS.name]) > 0

def test_nfs_cs_create(config):
    nas, pool, system = config
    NTP.create(system)

    assert not is_nfs_existed(nas)

    NFS_CS.create(nas)
    #nothing because the are no created dependencies
    assert not is_nfs_existed(nas)

    kerberos = KERBEROS.create(nas)
    NFS_CS.create(nas)
    assert not kerberos() is None
    assert not is_nfs_existed(nas)

    nis = NIS.create(nas)
    nfs = NFS_CS.create(nas)
    assert not nis() is None
    assert not nfs() is None
    assert is_nfs_existed(nas)
    assert nfs().parent == nas()
    assert nfs().name == NFS.name
    assert nfs().type == NFS_CS.name
    assert nfs().terminal

    other = NFS_CS.create(nas)
    assert other is None
    assert is_nfs_existed(nas)

    other = NFS_WS.create(nas)
    assert other is None
    assert is_nfs_existed(nas)

def test_nfs_ws_create(config):
    nas, pool, system = config

    assert not is_nfs_existed(nas)

    NFS_WS.create(nas)
    assert not is_nfs_existed(nas)

    nis = NIS.create(nas)
    NFS_WS.create(nas)
    assert not nis() is None
    assert not is_nfs_existed(nas)

    ntp = NTP.create(system)
    dns = DNS.create(nas)
    fi = FI.create(nas)
    cifs = CIFS_J.create(nas)
    nfs = NFS_WS.create(nas)
    assert not ntp() is None
    assert not dns() is None
    assert not cifs() is None
    assert not fi() is None
    assert not nfs() is None
    assert is_nfs_existed(nas)
    assert nfs().parent == nas
    assert nfs().name == NFS.name
    assert nfs().type == NFS_WS.name
    assert nfs().terminal

    other = NFS_WS.create(nas)
    assert other is None
    assert is_nfs_existed(nas)

    other = NFS_CS.create(nas)
    assert other is None
    assert is_nfs_existed(nas)

def test_nfs_cs_different_create(config):
    nas1, pool, system = config
    nas2 = NAS.create(pool)
    NTP.create(system)

    KERBEROS.create(nas1)
    KERBEROS.create(nas2)
    NIS.create(nas1)
    NIS.create(nas2)

    assert not is_nfs_existed(nas1)
    assert not is_nfs_existed(nas2)

    nfs2 = NFS_CS.create(nas2)
    assert not nfs2() is None
    assert not is_nfs_existed(nas1)
    assert is_nfs_existed(nas2)
    assert nfs2().parent == nas2

    nfs1 = NFS_CS.create(nas1)
    assert not nfs1() is None
    assert not nfs2() is None
    assert is_nfs_existed(nas1)
    assert is_nfs_existed(nas2)

def test_nfs_cs_ws_on_one_nas(config):
    nas, pool, system = config

    NTP.create(system)
    DNS.create(nas)
    FI.create(nas)
    NIS.create(nas)
    CIFS_J.create(nas)

    assert not is_nfs_existed(nas)

    nfs = NFS_CS.create(nas)
    assert nfs is None

    nfs = NFS_WS.create(nas)
    assert not nfs() is None

    NFS_WS.delete(nfs)

    assert not is_nfs_existed(nas)

    kerberos = KERBEROS.create(nas)
    assert not kerberos() is None

    nfs = NFS_CS.create(nas)
    assert not nfs() is None
    assert is_nfs_existed(nas)

def test_nfs_ws_wrong(config):
    nas, pool, system = config

    NTP.create(system)
    DNS.create(nas)
    FI.create(nas)
    NIS.create(nas)

    assert len(CIFS.list()) == 0
    assert len(NFS_WS.list()) == 0

    cifs = CIFS_J.create(nas)
    nfs = NFS_WS.create(nas)
    assert len(CIFS.list()) == 1
    assert len(NFS_WS.list()) == 1

    nfs().delete()
    cifs().delete()

    assert len(CIFS.list()) == 0
    assert len(NFS_WS.list()) == 0

    CIFS_SA.create(nas)
    NFS_WS.create(nas)
    assert len(CIFS.list()) == 1
    assert len(NFS_WS.list()) == 0
