from model.model_fixtures import *
import pytest

@pytest.yield_fixture(scope="function")
def config(pool, nas):
    try:
        yield [nas, pool]
    finally:
        pool().delete()

def test_snap_nfs_create(config):
    nas, pool = config
    NFS.create(nas)

    fs = FS_NFS.create(nas)
    assert not fs() is None
    assert len(SNAP_NFS.list()) == 0

    snap = SNAP_NFS.create(fs)
    assert not snap() is None
    assert snap().parent.parent == fs()
    assert snap().name == SNAP.name
    assert snap().type == SNAP_NFS.name
    assert len(SNAP_NFS.list()) == 1

    SNAP_NFS.create(fs)
    assert len(SNAP_NFS.list()) == 2
    assert len(SNAP.list()) == 2

def test_snap_nfs_modify(config):
    nas, pool = config
    NFS.create(nas)

    fs = FS_NFS.create(nas)
    assert not fs() is None
    assert len(SNAP_NFS.list()) == 0

    snap = SNAP_NFS.create(fs)
    assert len(SNAP_NFS.list()) == 1

    snap().modify(size = 1024)
    assert snap().size == 1024

def test_snap_nfs_delete(config):
    nas, pool = config
    NFS.create(nas)

    fs = [FS_NFS.create(nas) for _ in range(2)]

    assert not fs[0]() is None
    assert not fs[0]() is None
    assert len(SNAP_NFS.list()) == 0

    snap = [SNAP_NFS.create(fs[inx % 2]) for inx in range(4)]
    assert len(SNAP_NFS.list()) == 4
    for inx in range(4):
        assert snap[inx]().parent.parent == fs[inx % 2]

    snap[1]().delete()
    snap[2]().delete()

    assert snap[1]() is None
    assert snap[2]() is None
    assert len(SNAP_NFS.list()) == 2

    snap[0]().delete()
    snap[3]().delete()
    assert snap[0]() is None
    assert snap[3]() is None
    assert len(SNAP_NFS.list()) == 0

    snap = [SNAP_NFS.create(fs[inx % 2]) for inx in range(4)]
    assert len(SNAP_NFS.list()) == 4
    assert len(SNAP.list()) == 4
    for inx in range(4):
        assert snap[inx]().parent.parent == fs[inx % 2]
