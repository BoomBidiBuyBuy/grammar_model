from model.model_fixtures import *
import pytest

@pytest.yield_fixture(scope="function")
def config(pool, ntp, nas):
    try:
        yield [nas, pool, SYSTEM]
    finally:
        pool().delete()
        ntp().delete()

def test_fs_mup_create(config):
    nas, pool, system = config
    FI.create(nas)
    DNS.create(nas)

    assert len(FS.list()) == 0

    # NFS and CIFS are not created
    FS_MUP.create(nas)
    assert len(FS.list()) == 0

    nfs = NFS.create(nas)
    FS_MUP.create(nas)
    assert len(FS.list()) == 0

    cifs = CIFS_J.create(nas)
    fs = FS_MUP.create(nas)
    assert len(FS.list()) == 1
    assert fs().type == FS_MUP.name
    assert fs().name == FS.name
    assert fs().parent.parent == nas()

    cifs().delete()
    FS_MUP.create(nas)
    assert len(FS.list()) == 1

    CIFS_SA.create(nas)
    FS_MUP.create(nas)
    assert len(FS.list()) == 2

def test_fs_mup_modify(config):
    nas, pool, system = config
    FI.create(nas)
    DNS.create(nas)
    NFS.create(nas)
    CIFS_J.create(nas)
    assert len(FS.list()) == 0

    fs = FS_MUP.create(nas)
    assert len(FS.list()) == 1

    fs().modify(size=1024)
    assert fs().size == 1024
    assert len(FS.list()) == 1

def test_fs_mup_delete(config):
    nas1, pool, system = config
    nas2 = NAS.create(pool)
    FI.create(nas1)
    DNS.create(nas1)
    NFS.create(nas1)
    NFS.create(nas2)
    CIFS_J.create(nas1)
    assert len(FS.list()) == 0

    mup_fs = FS_MUP.create(nas1)
    assert len(FS.list()) == 1

    nfs_fs1 = FS_NFS.create(nas2)
    assert len(FS.list()) == 2
    assert len(FS_MUP.list()) == 1

    nfs_fs2 = FS_NFS.create(nas1)
    assert len(FS.list()) == len(FS_MUP.list()) + len(FS_NFS.list())

    cifs_fs = FS_CIFS.create(nas1)
    assert len(FS_CIFS.list()) == 1
    assert len(FS.list()) == len(FS_MUP.list()) + \
                                len(FS_NFS.list()) + \
                                len(FS_CIFS.list())

    nfs_fs2().delete()
    assert len(FS_NFS.list()) == 1

    cifs_fs().delete()
    assert len(FS_CIFS.list()) == 0

    mup_fs().delete()
    assert len(FS_MUP.list()) == 0

    nas2().delete()
    assert len(FS.list()) == 0
