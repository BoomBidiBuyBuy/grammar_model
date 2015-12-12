from core.parser import *
import pytest
import os

@pytest.fixture(scope="module")
def config(request):
    path = os.path.dirname(__file__) + "\..\model\\"
    globals().update(load_model_file(path + "POOL.json"))
    globals().update(load_model_file(path + "NAS.json"))
    globals().update(load_model_file(path + "ASA.json"))

    system_node = Node(name="*", terminal=False)
    system_node.add(Node(POOL.name, terminal=False))

    pool = POOL.create(system_node)
    nas = NAS.create(pool)

    def finalizer():
        while len(ASA.list()):
            ASA.delete(ASA.list()[0])

        while len(NAS.list()):
            NAS.delete(NAS.list()[0])

        while len(POOL.list()):
            POOL.delete(POOL.list()[0])

    request.addfinalizer(finalizer)

    return [nas, pool, system_node]

def is_asa_existed(nas):
    return len([child for child in nas().children if child.name == ASA.name and child.terminal]) > 0

def test_asa_create(config):
    nas = config[0]

    assert len(ASA.list()) == 0
    assert not is_asa_existed(nas)

    asa = ASA.create(nas)

    assert len(ASA.list()) == 1
    assert asa().name == ASA.name
    assert asa().terminal
    assert hasattr(asa(), 'id')
    assert asa().parent == nas()
    assert is_asa_existed(nas)

    ASA.create(nas)

    assert len(ASA.list()) == 1

    # tear down
    ASA.delete(asa)

def test_asa_modify(config):
    nas = config[0]

    assert len(ASA.list()) == 0
    assert not is_asa_existed(nas)

    asa = ASA.create(nas)

    ASA.modify(asa)

    assert is_asa_existed(nas)
    assert len(ASA.list()) == 1
    assert asa().name == ASA.name
    assert asa().terminal
    assert hasattr(asa(), 'id')
    assert asa().parent == nas()

    # tear down
    ASA.delete(asa)

def test_asa_delete(config):
    nas1, pool, _ = config
    nas2 = NAS.create(pool)
    nas3 = NAS.create(pool)

    asa1 = ASA.create(nas1)

    assert asa1().parent == nas1()
    assert is_asa_existed(nas1)
    assert not is_asa_existed(nas2)
    assert not is_asa_existed(nas3)
    assert len(ASA.list()) == 1

    asa3 = ASA.create(nas3)

    assert asa3().parent == nas3()
    assert is_asa_existed(nas1)
    assert not is_asa_existed(nas2)
    assert is_asa_existed(nas3)
    assert len(ASA.list()) == 2

    asa2 = ASA.create(nas2)

    assert asa2().parent == nas2()
    assert is_asa_existed(nas1)
    assert is_asa_existed(nas2)
    assert is_asa_existed(nas3)
    assert len(ASA.list()) == 3

    ASA.delete(asa1)

    assert asa1() == None
    assert not is_asa_existed(nas1)
    assert len(ASA.list()) == 2

    asa1 = ASA.create(nas1)

    assert asa1().parent == nas1()
    assert is_asa_existed(nas1)
    assert len(ASA.list()) == 3

    ASA.delete(asa1)
    ASA.delete(asa2)
    ASA.delete(asa3)

    assert asa1() == None
    assert asa2() == None
    assert asa3() == None
    assert len(ASA.list()) == 0