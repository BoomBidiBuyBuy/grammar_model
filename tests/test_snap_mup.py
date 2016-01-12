from model.model_fixtures import *
import pytest

@pytest.yield_fixture(scope="function")
def config(pool, nas, ntp, dns, fi):
    try:
        yield [nas, pool]
    finally:
        pool().delete()

def test_snap_mup_create(config):
    nas, pool = config
    CIFS_J.create(nas)
    NFS.create(nas)

    fs = FS_MUP.create(nas)
    assert not fs() is None
    assert len(SNAP_MUP.list()) == 0

    snap = SNAP_MUP.create(fs)
    assert not snap() is None
    assert snap().parent.parent == fs()
    assert snap().name == SNAP.name
    assert snap().type == SNAP_MUP.name
    assert len(SNAP_MUP.list()) == 1

    SNAP_MUP.create(fs)
    assert len(SNAP_MUP.list()) == 2
    assert len(SNAP.list()) == 2

def test_snap_mup_modify(config):
    nas, pool = config
    CIFS_J.create(nas)
    NFS.create(nas)

    fs = FS_MUP.create(nas)
    assert not fs() is None
    assert len(SNAP_MUP.list()) == 0

    snap = SNAP_MUP.create(fs)
    assert len(SNAP_MUP.list()) == 1

    snap().modify(size = 1024)
    assert snap().size == 1024

def test_snap_mup_delete(config):
    nas, pool = config
    CIFS_J.create(nas)
    NFS.create(nas)

    fs = [FS_MUP.create(nas) for _ in range(2)]

    assert not fs[0]() is None
    assert not fs[0]() is None
    assert len(SNAP_MUP.list()) == 0

    snap = [SNAP_MUP.create(fs[inx % 2]) for inx in range(4)]
    assert len(SNAP_MUP.list()) == 4
    for inx in range(4):
        assert snap[inx]().parent.parent == fs[inx % 2]

    snap[1]().delete()
    snap[2]().delete()

    assert snap[1]() is None
    assert snap[2]() is None
    assert len(SNAP_MUP.list()) == 2

    snap[0]().delete()
    snap[3]().delete()
    assert snap[0]() is None
    assert snap[3]() is None
    assert len(SNAP_MUP.list()) == 0

    snap = [SNAP_MUP.create(fs[inx % 2]) for inx in range(4)]
    assert len(SNAP_MUP.list()) == 4
    assert len(SNAP.list()) == 4
    for inx in range(4):
        assert snap[inx]().parent.parent == fs[inx % 2]

def test_delete_all(config):
    nas, pool = config
    NFS.create(nas)
    CIFS_SA.create(nas)

    fs1 = FS_CIFS.create(nas)
    fs2 = FS_NFS.create(nas)
    fs3 = FS_MUP.create(nas)
    assert not fs1() is None
    assert not fs2() is None
    assert not fs3() is None

    snap1 = SNAP_CIFS.create(fs1)
    assert len(SNAP.list()) == 1
    snap2 = SNAP_NFS.create(fs2)
    assert len(SNAP.list()) == 2
    snap3 = SNAP_MUP.create(fs3)
    assert len(SNAP.list()) == 3

    [snap().delete() for snap in SNAP.list()]
    assert len(SNAP.list()) == 0
