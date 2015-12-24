from model.model_fixtures import *
import pytest

@pytest.yield_fixture(scope="function")
def config(pool_type, nas_type, nfs_cs_type, kerberos_type, nis_type):
    [globals().update(obj) for obj in [pool_type, nas_type, nfs_cs_type, kerberos_type, nis_type]]

    system_node = Node(name="*", terminal=False)
    system_node.add(Node(POOL.name, terminal=False))

    pool = POOL.create(system_node)
    nas = NAS.create(pool)

    try:
        yield [nas, pool, system_node]
    finally:
        while len(NAS.list()):
            NAS.delete(NAS.list()[0])

        while len(POOL.list()):
            POOL.delete(POOL.list()[0])

def is_nfs_existed(nas):
    return len([child for child in nas().children if child.name == NFS_CS.name]) > 0

def test_nfs_cs_create(config):
    nas, pool, system = config

    assert len(NFS_CS.list()) == 0
    assert not is_nfs_existed(nas)

    NFS_CS.create(nas)
    #nothing because the are no created dependencies
    assert len(NFS_CS.list()) == 0

    kerberos = KERBEROS.create(nas)
    NFS_CS.create(nas)
    assert not kerberos() is None
    assert len(NFS_CS.list()) == 0

    nis = NIS.create(nas)
    nfs = NFS_CS.create(nas)
    assert not nis() is None
    assert not nfs() is None
