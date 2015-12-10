from core.parser import *
import pytest
import os

@pytest.fixture(scope="module")
def config(request):
    path = os.path.dirname(__file__) + "\..\model\\"
    globals().update(load_model_file(path + "POOL.json"))
    globals().update(load_model_file(path + "NAS.json"))
    globals().update(load_model_file(path + "NDMP.json"))

    system_node = Node(name="*", terminal=False)
    system_node.add(Node(POOL.name, terminal=False))

    pool = POOL.create(system_node)
    nas = NAS.create(pool)

    def finalizer():
        while len(NDMP.list()):
            NDMP.delete(NDMP.list()[0])

        while len(NAS.list()):
            NAS.delete(NAS.list()[0])

        while len(POOL.list()):
            POOL.delete(POOL.list()[0])

    request.addfinalizer(finalizer)

    return [nas, pool, system_node]

def is_ndmp_existed(nas):
    return len([child for child in nas().children if child.name == NDMP.name and child.terminal]) > 0

def test_ndmp_create(config):
    nas = config[0]

    assert len(NDMP.list()) == 0
    assert not is_ndmp_existed(nas)

    ndmp = NDMP.create(nas)

    assert len(NDMP.list()) == 1
    assert ndmp().name == NDMP.name
    assert ndmp().terminal == True
    assert hasattr(ndmp(), 'id')
    assert ndmp().parent == nas()
    assert is_ndmp_existed(nas)

    NDMP.create(nas)

    assert len(NDMP.list()) == 1

    # tear down
    NDMP.delete(ndmp)

def test_ndmp_modify(config):
    nas = config[0]

    assert len(NDMP.list()) == 0
    assert not is_ndmp_existed(nas)

    ndmp = NDMP.create(nas)

    NDMP.modify(ndmp)

    assert is_ndmp_existed(nas)
    assert len(NDMP.list()) == 1
    assert ndmp().name == NDMP.name
    assert ndmp().terminal == True
    assert hasattr(ndmp(), 'id')
    assert ndmp().parent == nas()

    # tear down
    NDMP.delete(ndmp)

def test_ndmp_delete(config):
    nas1 = config[0]
    nas2 = NAS.create(config[1])
    nas3 = NAS.create(config[1])

    ndmp1 = NDMP.create(nas1)

    assert ndmp1().parent == nas1()
    assert is_ndmp_existed(nas1)
    assert not is_ndmp_existed(nas2)
    assert not is_ndmp_existed(nas3)
    assert len(NDMP.list()) == 1

    ndmp2 = NDMP.create(nas2)

    assert ndmp2().parent == nas2()
    assert ndmp1().parent == nas1()
    assert is_ndmp_existed(nas1)
    assert is_ndmp_existed(nas2)
    assert not is_ndmp_existed(nas3)
    assert len(NDMP.list()) == 2

    ndmp3 = NDMP.create(nas3)

    assert ndmp1().parent == nas1()
    assert ndmp2().parent == nas2()
    assert ndmp3().parent == nas3()
    assert is_ndmp_existed(nas1)
    assert is_ndmp_existed(nas2)
    assert is_ndmp_existed(nas3)

    NDMP.delete(ndmp1)
    assert ndmp1() == None
    assert not is_ndmp_existed(nas1)
    assert is_ndmp_existed(nas2)
    assert is_ndmp_existed(nas3)

    NDMP.delete(ndmp2)
    assert ndmp2() == None
    assert not is_ndmp_existed(nas1)
    assert not is_ndmp_existed(nas2)
    assert is_ndmp_existed(nas3)

    NDMP.delete(ndmp3)
    assert ndmp3() == None
    assert not is_ndmp_existed(nas1)
    assert not is_ndmp_existed(nas2)
    assert not is_ndmp_existed(nas3)

def test_middle(config):
    nas1, pool, _ = config
    nas2 = NAS.create(pool)
    nas3 = NAS.create(pool)

    ndmp = NDMP.create(nas2)

    assert ndmp().parent == nas2()
    assert is_ndmp_existed(nas2)
    assert not is_ndmp_existed(nas1)
    assert not is_ndmp_existed(nas3)

    NDMP.delete(ndmp)

    assert ndmp() == None
    assert not is_ndmp_existed(nas1)
    assert not is_ndmp_existed(nas2)
    assert not is_ndmp_existed(nas3)
