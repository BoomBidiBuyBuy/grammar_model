from core.parser import *
import pytest
import os

@pytest.fixture
def system_node(scope="module"):
    path = os.path.dirname(__file__) + "\..\model\POOL.json"
    globals().update(load_model_file(path))

    root_node = Node(name="*", terminal=False)
    root_node.add(Node(POOL.name, terminal=False))
    return root_node

def test_pool_create(system_node):
    root_node = system_node

    def check_pool(p):
        assert p() in root_node.children[0].children
        assert p().parent == root_node.children[0]
        assert p().name == 'POOL'
        assert p().terminal == True
        assert len(p().children) == 1 # NAS
        assert hasattr(p(), 'id')

        nas = weakref.ref(p().children[0])

        assert nas().name == 'NAS'
        assert nas().terminal == False
        assert nas().parent == p()
        assert len(nas().children) == 0

    assert len(root_node.children) == 1
    assert root_node.children[0].parent == root_node
    assert root_node.children[0].name == 'POOL'
    assert root_node.children[0].terminal == False
    assert len(root_node.children[0].children) == 0
    assert not hasattr(root_node.children[0], 'id')

    pool1 = POOL.create(root_node)

    assert len(POOL.list()) == 1
    assert len(root_node.children[0].children) == 1
    check_pool(pool1)

    pool2 = POOL.create(root_node)
    assert len(root_node.children[0].children) == 2
    check_pool(pool2)

    pool3 = POOL.create(root_node)
    assert len(root_node.children[0].children) == 3
    check_pool(pool3)

    # return to the begin state
    del OBJECTS[POOL.name]
    del root_node.children[0]
    root_node.add(Node(POOL.name, terminal=False))

def test_pool_modify(system_node):
    root_node = system_node

    pool = POOL.create(root_node)

    old_name = str(pool().name)
    old_terminal = bool(pool().terminal)
    old_id = str(pool().id)

    POOL.modify(pool)

    assert len(root_node.children) == 1
    assert len(root_node.children[0].children) == 1

    assert pool() == root_node.children[0].children[0]
    assert pool().parent == root_node.children[0]
    assert pool().name == old_name
    assert pool().id == old_id
    assert pool().terminal == old_terminal
    assert len(pool().children) == 1

    nas = weakref.ref(pool().children[0])

    assert nas().name == 'NAS'
    assert nas().terminal == False
    assert nas().parent == pool()
    assert len(nas().children) == 0

    # return to the begin state
    del OBJECTS[POOL.name]
    del root_node.children[0]
    root_node.add(Node(POOL.name, terminal=False))

def test_pool_delete(system_node):
    root_node = system_node

    pool = weakref.ref(root_node.children[0])

    pool1 = POOL.create(root_node)
    pool2 = POOL.create(root_node)
    pool3 = POOL.create(root_node)

    assert len(pool().children) == 3

    POOL.delete(pool1)

    assert pool1() is None
    assert len(pool().children) == 2
    assert pool2() in pool().children
    assert pool3() in pool().children
    assert pool2().parent == pool()
    assert pool3().parent == pool()

    POOL.delete(pool2)

    assert pool2() is None
    assert len(pool().children) == 1
    assert pool3() in pool().children
    assert pool3().parent == pool()

    POOL.delete(pool3)

    assert pool3() is None
    assert len(pool().children) == 0

