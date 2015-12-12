from core.parser import *
import pytest
import os

@pytest.fixture(scope="module")
def config(request):
    path = os.path.dirname(__file__) + "\..\model\\"
    globals().update(load_model_file(path + "POOL.json"))
    globals().update(load_model_file(path + "NAS.json"))
    globals().update(load_model_file(path + "NIS.json"))

    system_node = Node(name="*", terminal=False)
    system_node.add(Node(POOL.name, terminal=False))

    pool = POOL.create(system_node)
    nas = NAS.create(pool)

    def finalizer():
        while len(NIS.list()):
            NIS.delete(NIS.list()[0])

        while len(NAS.list()):
            NAS.delete(NAS.list()[0])

        while len(POOL.list()):
            POOL.delete(POOL.list()[0])

    request.addfinalizer(finalizer)

    return [nas, pool, system_node]

def is_nis_existed(nas):
    return len([child for child in nas().children if child.name == NIS.name and child.terminal]) > 0

def test_nis_create(config):
    nas = config[0]

    assert len(NIS.list()) == 0
    assert not is_nis_existed(nas)

    nis = NIS.create(nas)

    assert len(NIS.list()) == 1
    assert nis().name == NIS.name
    assert nis().terminal == True
    assert hasattr(nis(), 'id')
    assert nis().parent == nas()
    assert is_nis_existed(nas)

    NIS.create(nas)

    assert len(NIS.list()) == 1

    # tear down
    NIS.delete(nis)

def test_nis_modify(config):
    nas = config[0]

    assert len(NIS.list()) == 0
    assert not is_nis_existed(nas)

    nis = NIS.create(nas)

    NIS.modify(nis)

    assert is_nis_existed(nas)
    assert len(NIS.list()) == 1
    assert nis().name == NIS.name
    assert nis().terminal == True
    assert hasattr(nis(), 'id')
    assert nis().parent == nas()

    # tear down
    NIS.delete(nis)

def test_nis_delete(config):
    nas1 = config[0]
    nas2 = NAS.create(config[1])
    nas3 = NAS.create(config[1])

    nis2 = NIS.create(nas2)

    assert nis2().parent == nas2()
    assert is_nis_existed(nas2)
    assert not is_nis_existed(nas1)
    assert not is_nis_existed(nas3)
    assert len(NIS.list()) == 1

    nis1 = NIS.create(nas1)

    assert nis1().parent == nas1()
    assert is_nis_existed(nas1)
    assert is_nis_existed(nas2)
    assert not is_nis_existed(nas3)
    assert len(NIS.list()) == 2

    nis3 = NIS.create(nas3)

    assert nis3().parent == nas3()
    assert is_nis_existed(nas1)
    assert is_nis_existed(nas2)
    assert is_nis_existed(nas3)
    assert len(NIS.list()) == 3

    NIS.delete(nis1)

    assert nis1() == None
    assert not is_nis_existed(nas1)
    assert len(NIS.list()) == 2

    NIS.delete(nis2)

    assert nis2() == None
    assert not is_nis_existed(nas2)
    assert len(NIS.list()) == 1

    NIS.delete(nis3)

    assert nis3() == None
    assert not is_nis_existed(nas3)
    assert len(NIS.list()) == 0

    nis3 = NIS.create(nas3)

    assert nis3().parent == nas3()
    assert is_nis_existed(nas3)
    assert len(NIS.list()) == 1

    NIS.delete(nis3)