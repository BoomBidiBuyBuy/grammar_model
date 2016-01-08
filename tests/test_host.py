from model.model_fixtures import *
import pytest

@pytest.yield_fixture(scope="function")
def config(pool, nas):
    try:
        yield [nas, pool]
    finally:
        pool().delete()

def test_host_create(config):
    nas, pool = config
    NFS.create(nas)

    fs = FS_NFS.create(nas)
    sh = SH_NFS.create(fs)
    assert not fs() is None
    assert not sh() is None
    assert len(HOST.list()) == 0

    host = HOST.create(sh)
    assert not host() is None
    assert host().parent.parent == sh()
    assert len(HOST.list()) == 1

    host2 = HOST.create(sh)
    host3 = HOST.create(sh)
    assert not host2() is None
    assert not host3() is None
    assert len(HOST.list()) == 3

def test_host_modify(config):
    nas, pool = config
    NFS.create(nas)

    fs = FS_NFS.create(nas)
    sh = SH_NFS.create(fs)
    host = HOST.create(sh, address="1.1.1.1")
    assert host().address == '1.1.1.1'

    host().modify(address="1.2.3.4")
    assert host().address == '1.2.3.4'

def test_host_delete(config):
    nas, pool = config
    NFS.create(nas)

    fs = FS_NFS.create(nas)
    sh = SH_NFS.create(fs)
    host = HOST.create(sh)
    assert not host() is None
    assert len(HOST.list()) == 1

    host().delete()
    assert host() is None
    assert len(HOST.list()) == 0
