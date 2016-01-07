from model.model_fixtures import *
import pytest

@pytest.yield_fixture(scope="function")
def config(nas, ntp, pool):
    try:
        yield [nas, pool, SYSTEM]
    finally:
        while len(POOL.list()):
            POOL.list()[0]().delete()

        ntp().delete()

def test_fs_cifs_create(config):
    nas, pool, system = config
    FI.create(nas)
    DNS.create(nas)

    assert len(FS.list()) == 0

    # no CIFS is created
    FS_CIFS.create(nas)
    assert len(FS.list()) == 0

    cifs = CIFS_SA.create(nas)
    fs1 = FS_CIFS.create(nas)
    assert len(FS.list()) == 1
    assert len(FS_CIFS.list()) == 1
    assert fs1().type == FS_CIFS.name
    assert fs1().name == FS.name
    assert fs1().parent.parent == nas()

    fs2 = FS_CIFS.create(nas)
    assert len(FS_CIFS.list()) == 2

    cifs().delete()
    FS_CIFS.create(nas)
    assert len(FS_CIFS.list()) == 2

    fs1().delete()
    fs2().delete()
    assert len(FS_CIFS.list()) == 2

    CIFS_J.create(nas)
    FS_CIFS.create(nas)
    assert len(FS_CIFS.list()) == 3

def test_fs_cifs_delete(config):
    nas1, pool, system = config
    nas2 = NAS.create(pool)

    FI.create(nas1), FI.create(nas2)
    DNS.create(nas1), DNS.create(nas2)
    CIFS_SA.create(nas1), CIFS_J.create(nas2)

    fs1 = FS_CIFS.create(nas1)
    fs2 = FS_CIFS.create(nas1)
    fs3 = FS_CIFS.create(nas2)
    fs4 = FS_CIFS.create(nas2)

    assert len(FS_CIFS.list()) == 4
    assert len(FS.list()) == 4

    fs2().delete()
    fs3().delete()

    assert len(FS_CIFS.list()) == 2
    assert len(FS.list()) == 2

    [FS_CIFS.create(nas2) for _ in range(5)]

    assert len(FS_CIFS.list()) == 7
    assert len(FS.list()) == 7

    nas2().delete()

    assert len(FS_CIFS.list()) == 1
    assert len(FS.list()) == 1

    pool().delete()

    assert len(FS_CIFS.list()) == 0
    assert len(FS.list()) == 0


