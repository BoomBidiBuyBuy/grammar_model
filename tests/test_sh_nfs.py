from model.model_fixtures import *
import pytest

@pytest.yield_fixture(scope="function")
def config(pool, nas, ntp, fi, dns):
    try:
        yield [nas, pool]
    finally:
        pool().delete()

def test_sh_nfs_create(config):
    nas, pool = config
    NFS.create(nas)
    CIFS_J.create(nas)

    fs_nfs = FS_NFS.create(nas)
    fs_mup = FS_MUP.create(nas)

    assert not fs_nfs() is None
    assert not fs_mup() is None

    assert len(SH_NFS.list()) == 0

    sh = SH_NFS.create(fs_nfs)

    assert not sh() is None
    assert len(SH_NFS.list()) == 1
    assert sh().parent.parent == fs_nfs()
    assert sh().name == SH_NFS.name

    sh_mup = SH_NFS.create(fs_mup)

    assert not sh_mup() is None
    assert len(SH_NFS.list()) == 2
    assert sh_mup().parent.parent == fs_mup()

    SH_NFS.create(fs_nfs)
    assert len(SH_NFS.list()) == 3
    SH_NFS.create(fs_mup)
    assert len(SH_NFS.list()) == 4

def test_sh_nfs_modify(config):
    nas, pool = config
    CIFS_J.create(nas)
    NFS.create(nas)

    fs = FS_NFS.create(nas)
    fs_mup = FS_MUP.create(nas)

    sh1 = SH_NFS.create(fs)
    sh2 = SH_NFS.create(fs_mup)

    sh1().modify(path="/abc")
    assert sh1().path == "/abc"
    sh2().modify(path="/my_folder")
    assert sh2().path == "/my_folder"

def test_sh_nfs_delete(config):
    nas, pool = config
    CIFS_J.create(nas)
    NFS.create(nas)

    fs = FS_NFS.create(nas)
    fs_mup = FS_MUP.create(nas)

    assert len(SH_NFS.list()) == 0

    sh1 = SH_NFS.create(fs)
    sh2 = SH_NFS.create(fs)
    sh3 = SH_NFS.create(fs_mup)
    sh4 = SH_NFS.create(fs_mup)
    assert len(SH_NFS.list()) == 4

    sh2().delete()
    assert len(SH_NFS.list()) == 3
    assert sh2() is None
    assert sh1().parent.parent == fs()

    sh3().delete()
    assert len(SH_NFS.list()) == 2
    assert sh3() is None
    assert sh4().parent.parent == fs_mup()

    sh1().delete()
    assert len(SH_NFS.list()) == 1
    assert sh1() is None

    sh4().delete()
    assert len(SH_NFS.list()) == 0
    assert sh4() is None

def test_sh_nfs_snap(config):
    nas, pool = config
    NFS.create(nas)

    fs = FS_NFS.create(nas)
    snap = SNAP_NFS.create(fs)

    assert not fs() is None
    assert not snap() is None
    assert len(SH_NFS.list()) == 0

    sh1 = SH_NFS.create(fs)
    sh2 = SH_NFS.create(snap)

    assert len(SH_NFS.list()) == 2
    assert not sh1() is None
    assert not sh2() is None
    assert sh1().parent.parent == fs()
    assert sh2().parent.parent == snap()

    sh3 = SH_NFS.create(snap)
    assert len(SH_NFS.list()) == 3
    assert sh3().parent.parent == snap()