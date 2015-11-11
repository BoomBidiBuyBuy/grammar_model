from core.parser import *
import pytest
import os

@pytest.fixture
def pool_nodes(scope="module"):
    path = os.path.dirname(__file__) + "\..\model\\"
    globals().update(load_model_file(path + "POOL.json"))
    globals().update(load_model_file(path + "NAS.json"))

    system_node = Node(name="*", terminal=False)
    system_node.add(Node(POOL.name, terminal=False))

    pool1 = POOL.create(system_node)
    pool2 = POOL.create(system_node)

    return (pool1, pool2)

def check_nas(nas, pool):
    assert nas in pool.children[0].children
    assert nas.parent == pool.children[0]
    assert nas.name == 'NAS'
    assert nas.terminal == True
    assert len(nas.children)  == 11
    assert hasattr(nas, 'id')

def test_nas_create1(pool_nodes):
    pool, _ = pool_nodes
    pool = pool()

    assert len(pool.children) == 1
    assert pool.children[0].parent == pool
    assert pool.children[0].name == 'NAS'
    assert pool.children[0].terminal == False
    assert len(pool.children[0].children) == 0
    assert not hasattr(pool.children[0], 'id')

    nas1 = NAS.create(pool)

    # check that creation doesn't break the parent object
    assert len(pool.children) == 1
    assert pool.children[0].parent == pool
    assert pool.children[0].name == 'NAS'

    # check that it's really created
    assert len(NAS.list()) == 1
    assert len(pool.children[0].children) == 1
    check_nas(nas1(), pool)

    nas2 = NAS.create(pool)
    assert len(NAS.list()) == 2
    assert len(pool.children[0].children) == 2
    check_nas(nas2(), pool)

    nas3 = NAS.create(pool)
    assert len(NAS.list()) == 3
    assert len(pool.children[0].children) == 3
    check_nas(nas3(), pool)

    # return to the begin state
    del OBJECTS[NAS.name]
    del pool.children[0]
    pool.add(Node(NAS.name, terminal=False))

def test_nas_create2(pool_nodes):
    pool1, pool2 = pool_nodes
    pool1, pool2 = pool1(), pool2()

    p1_nas1 = NAS.create(pool1)
    p1_nas2 = NAS.create(pool1)
    p1_nas3 = NAS.create(pool1)

    p2_nas1 = NAS.create(pool2)
    p2_nas2 = NAS.create(pool2)

    assert len(NAS.list()) == 5
    assert len(pool1.children[0].children) == 3
    assert len(pool2.children[0].children) == 2

    for nas in [p1_nas1, p1_nas2, p1_nas3]:
        check_nas(nas(), pool1)

    for nas in [p2_nas1, p2_nas2]:
        check_nas(nas(), pool2)

    # return to the begin state
    del OBJECTS[NAS.name]
    del pool1.children[0]
    del pool2.children[0]
    pool1.add(Node(NAS.name, terminal=False))
    pool2.add(Node(NAS.name, terminal=False))


def test_nas_modify(pool_nodes):
    pass

def test_nas_delete_on_one_pool(pool_nodes):
    pool, _ = pool_nodes
    pool = pool()

    nas = weakref.ref(pool.children[0])

    nas1 = NAS.create(pool)
    nas2 = NAS.create(pool)
    nas3 = NAS.create(pool)

    assert len(pool.children[0].children) == 3

    NAS.delete(nas1)

    assert nas1() is None
    assert len(pool.children[0].children) == 2
    assert nas2() in nas().children
    assert nas3() in nas().children

    NAS.delete(nas3)

    assert nas1() == None
    assert nas3() == None
    assert len(pool.children[0].children) == 1
    assert nas2() in nas().children

    NAS.delete(nas2)

    assert nas2() == None
    assert len(pool.children[0].children) == 0

def test_nas_delete_on_different_pools(pool_nodes):
    pool1, pool2 = pool_nodes
    pool1, pool2 = pool1(), pool2()

    nas1 = NAS.create(pool1)
    nas2 = NAS.create(pool1)
    nas3 = NAS.create(pool1)

    nas4 = NAS.create(pool2)
    nas5 = NAS.create(pool2)

    assert len(pool1.children[0].children) == 3
    assert len(pool2.children[0].children) == 2

    NAS.delete(nas1)

    assert len(pool1.children[0].children) == 2
    assert len(pool2.children[0].children) == 2

    NAS.delete(nas4)

    assert len(pool1.children[0].children) == 2
    assert len(pool2.children[0].children) == 1

    NAS.delete(nas2)

    assert len(pool1.children[0].children) == 1
    assert len(pool2.children[0].children) == 1

    NAS.delete(nas5)

    assert len(pool1.children[0].children) == 1
    assert len(pool2.children[0].children) == 0

    NAS.delete(nas3)

    assert len(pool1.children[0].children) == 0
    assert len(pool2.children[0].children) == 0

def test_nas_delete_pool(pool_nodes):
    pool1, pool2 = pool_nodes

    nas1 = NAS.create(pool1)
    nas2 = NAS.create(pool1)
    nas3 = NAS.create(pool1)

    nas4 = NAS.create(pool2)
    nas5 = NAS.create(pool2)

    assert len(pool1().children[0].children) == 3
    assert len(pool2().children[0].children) == 2
    assert len(NAS.list()) == 5
    assert len(POOL.list()) == 2

    POOL.delete(pool1)

    assert len(NAS.list()) == 2
    assert len(POOL.list()) == 1
    assert pool1() is None
    assert nas1() is None
    assert nas2() is None
    assert nas3() is None
    assert len(pool2().children[0].children) == 2
    assert not nas4() is None
    assert not nas5() is None

    POOL.delete(pool2)

    assert len(NAS.list()) == 0
    assert len(POOL.list()) == 0
    assert pool2() is None
    assert nas4() is None
    assert nas5() is None


