from model.model_fixtures import *
import pytest

@pytest.yield_fixture(scope="function")
def config(pool, nas, ntp, fi, dns):
    try:
        yield [nas, pool]
    finally:
        pool().delete()

def test_sh_cifs_create(config):
    nas, pool = config
    NFS.create(nas)
    CIFS_J.create(nas)

    fs_cifs = FS_CIFS.create(nas)
    fs_mup = FS_MUP.create(nas)

    assert not fs_cifs() is None
    assert not fs_mup() is None
    assert len(SH_CIFS.list()) == 0

    sh = SH_CIFS.create(fs_cifs)
    assert not sh() is None
    assert len(SH_CIFS.list()) == 1
    assert sh().parent.parent == fs_cifs()
    assert sh().name == SH.name
    assert sh().type == SH_CIFS.name

    sh_mup = SH_CIFS.create(fs_mup)
    assert not sh_mup() is None
    assert len(SH_CIFS.list()) == 2
    assert sh_mup().parent.parent == fs_mup()
    assert sh_mup().name == SH.name
    assert sh_mup().type == SH_CIFS.name

    SH_CIFS.create(fs_cifs)
    assert len(SH_CIFS.list()) == 3
    SH_CIFS.create(fs_mup)
    assert len(SH_CIFS.list()) == 4
    assert len(SH.list()) == 4

def test_sh_cifs_modify(config):
    nas, pool = config
    NFS.create(nas)
    CIFS_J.create(nas)

    fs_cifs = FS_CIFS.create(nas)
    fs_mup = FS_MUP.create(nas)

    sh1 = SH_CIFS.create(fs_cifs)
    sh2 = SH_CIFS.create(fs_mup)

    sh1().modify(path="/abc")
    assert sh1().path == "/abc"
    sh2().modify(path="/my_folder")
    assert sh2().path == "/my_folder"

def test_sh_cifs_delete(config):
    nas, pool = config
    NFS.create(nas)
    CIFS_J.create(nas)

    fs_cifs = FS_CIFS.create(nas)
    fs_mup = FS_MUP.create(nas)

    sh1 = SH_CIFS.create(fs_cifs)
    sh2 = SH_CIFS.create(fs_cifs)
    sh3 = SH_CIFS.create(fs_mup)
    sh4 = SH_CIFS.create(fs_mup)

    assert len(SH_CIFS.list()) == 4

    sh2().delete()
    assert sh2() is None
    assert len(SH_CIFS.list()) == 3

    sh3().delete()
    assert sh3() is None
    assert len(SH_CIFS.list()) == 2

    assert sh1().parent.parent == fs_cifs()
    assert sh4().parent.parent == fs_mup()

    sh1().delete()
    sh4().delete()
    assert len(SH_CIFS.list()) == 0

def test_sh_mup(config):
    nas, pool = config
    NFS.create(nas)
    CIFS_J.create(nas)

    fs = FS_MUP.create(nas)

    assert len(SH_CIFS.list()) == 0
    assert len(SH_NFS.list()) == 0

    nfs_sh1 = SH_NFS.create(fs)
    cifs_sh1 = SH_CIFS.create(fs)

    assert len(SH_CIFS.list()) == 1
    assert len(SH_NFS.list()) == 1

    nfs_sh2 = SH_NFS.create(fs)
    cifs_sh2 = SH_CIFS.create(fs)

    assert len(SH_CIFS.list()) == 2
    assert len(SH_NFS.list()) == 2

    nfs_sh1().delete()
    cifs_sh1().delete()

    assert len(SH_CIFS.list()) == 1
    assert len(SH_NFS.list()) == 1

    nfs_sh2().delete()
    cifs_sh2().delete()

    assert len(SH_CIFS.list()) == 0
    assert len(SH_NFS.list()) == 0

def test_sh_cifs_snap(config):
    nas, pool = config
    CIFS_J.create(nas)

    fs = FS_CIFS.create(nas)
    snap = SNAP_CIFS.create(fs)

    assert not fs() is None
    assert not snap() is None
    assert len(SH_CIFS.list()) == 0

    sh1 = SH_CIFS.create(fs)
    sh2 = SH_CIFS.create(snap)

    assert len(SH_CIFS.list()) == 2
    assert not sh1() is None
    assert not sh2() is None
    assert sh1().parent.parent == fs()
    assert sh2().parent.parent == snap()

    sh3 = SH_CIFS.create(snap)
    assert len(SH_CIFS.list()) == 3
    assert sh3().parent.parent == snap()

def test_sh_mup_snap(config):
    nas, pool = config
    CIFS_J.create(nas)
    NFS.create(nas)

    fs = FS_MUP.create(nas)
    snap = SNAP_MUP.create(fs)

    assert not fs() is None
    assert not snap() is None
    assert len(SH_NFS.list()) == 0
    assert len(SH_CIFS.list()) == 0

    nfs_sh1 = SH_NFS.create(fs)
    nfs_sh2 = SH_NFS.create(snap)

    assert len(SH_NFS.list()) == 2
    assert not nfs_sh1() is None
    assert not nfs_sh2() is None
    assert nfs_sh1().parent.parent == fs()
    assert nfs_sh2().parent.parent == snap()

    cifs_sh1 = SH_CIFS.create(fs)
    cifs_sh2 = SH_CIFS.create(snap)

    assert len(SH_CIFS.list()) == 2
    assert not cifs_sh1() is None
    assert not cifs_sh2() is None
    assert cifs_sh1().parent.parent == fs()
    assert cifs_sh2().parent.parent == snap()

    nfs_sh3 = SH_NFS.create(snap)
    cifs_sh3 = SH_CIFS.create(snap)
    assert len(SH_CIFS.list()) == 3
    assert len(SH_NFS.list()) == 3
    assert len(SH.list()) == 6
    assert not nfs_sh3() is None
    assert not cifs_sh3() is None
    assert cifs_sh3().parent.parent == snap()
    assert nfs_sh3().parent.parent == snap()
