from model.model_fixtures import *
import pytest

@pytest.yield_fixture(scope="function")
def config(pool, ntp, nas):
    try:
        yield [nas, pool, SYSTEM]
    finally:
        pool().delete()
        ntp().delete()

def test_fs_nfs_create(config):
    nas, pool, system = config
    FI.create(nas)
    DNS.create(nas)

    assert len(FS.list()) == 0

    # NFS isn't created
    FS_NFS.create(nas)
    assert len(FS.list()) == 0

    nfs = NFS.create(nas)
    fs1 = FS_NFS.create(nas)
    assert len(FS.list()) == 1
    assert len(FS_NFS.list()) == 1
    assert fs1().type == FS_NFS.name
    assert fs1().name == FS.name
    assert fs1().parent.parent == nas()

    fs2 = FS_NFS.create(nas)
    assert len(FS.list()) == 2
    assert len(FS_NFS.list()) == 2

    nfs().delete()
    FS_NFS.create(nas)
    assert len(FS.list()) == 2
    assert len(FS_NFS.list()) == 2

    KERBEROS.create(nas)
    NIS.create(nas)
    nfs = NFS_CS.create(nas)
    FS_NFS.create(nas)
    assert len(FS.list()) == 3
    assert len(FS_NFS.list()) == 3

    nfs().delete()
    CIFS_J.create(nas)
    nfs = NFS_WS.create(nas)
    FS_NFS.create(nas)
    assert len(FS.list()) == 4
    assert len(FS_NFS.list()) == 4

def test_fs_nfs_delete(config):
    nas1, pool, system = config
    nas2 = NAS.create(pool)
    NFS.create(nas1), NFS.create(nas2)

    assert len(FS.list()) == 0

    fs1, fs2 = FS_NFS.create(nas1), FS_NFS.create(nas1)
    fs3, fs4 = FS_NFS.create(nas2), FS_NFS.create(nas2)

    assert fs1().parent.parent == nas1()
    assert fs3().parent.parent == nas2()
    assert len(FS.list()) == 4
    assert len(FS_NFS.list()) == 4

    fs2().delete()
    fs4().delete()

    assert len(FS.list()) == 2
    assert len(FS_NFS.list()) == 2

    nas2().delete()
    assert len(FS.list()) == 1
    assert len(FS_NFS.list()) == 1

def test_fs_cifs_nfs(config):
    nas, pool, system = config

    FI.create(nas)
    NFS.create(nas)
    CIFS_SA.create(nas)

    assert len(FS.list()) == 0

    fs1 = FS_NFS.create(nas)
    fs2 = FS_CIFS.create(nas)

    assert len(FS.list()) == 2
    assert len(FS_NFS.list()) == 1
    assert len(FS_CIFS.list()) == 1

    fs2().delete()
    assert len(FS.list()) == 1
    assert len(FS_CIFS.list()) == 0
    assert len(FS_NFS.list()) == 1