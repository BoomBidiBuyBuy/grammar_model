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
    assert sh().name == SH_CIFS.name

    sh_mup = SH_CIFS.create(fs_mup)
    assert not sh_mup() is None
    assert len(SH_CIFS.list()) == 2
    assert sh_mup().parent.parent == fs_mup()
    assert sh_mup().name == SH_CIFS.name

    SH_CIFS.create(fs_cifs)
    assert len(SH_CIFS.list()) == 3
    SH_CIFS.create(fs_mup)
    assert len(SH_CIFS.list()) == 4

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