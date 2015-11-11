from core.parser import *
import pytest
import os

@pytest.fixture
def system_node(scope="module"):
    path = os.path.dirname(__file__) + "\..\model\\"
    globals().update(load_model_file(path + "NTP.json"))

    system_node = Node(name="*", terminal=False)
    system_node.add(Node(NTP.name, terminal=False))
    return system_node

def test_ntp_create(system_node):
    root_node = system_node

    assert len(root_node.children) == 1
    assert root_node.children[0].parent == root_node
    assert root_node.children[0].name == 'NTP'
    assert root_node.children[0].terminal == False
    assert len(root_node.children[0].children) == 0
    assert not hasattr(root_node.children[0], 'id')

    ntp = NTP.create(root_node)

    assert len(root_node.children) == 1
    assert ntp() == root_node.children[0]
    assert ntp().parent == root_node
    assert ntp().name == 'NTP'
    assert ntp().terminal == True
    assert len(ntp().children) == 0
    assert hasattr(ntp(), 'id')

    assert NTP.create(root_node) is None

    # return to begin state
    del OBJECTS[ntp().name][ntp().id]
    del root_node.children[0]
    root_node.add(Node(NTP.name, terminal=False))

def test_ntp_modify(system_node):
    root_node = system_node

    ntp = NTP.create(root_node)

    old_name = str(ntp().name)
    old_terminal = bool(ntp().terminal)
    old_id = str(ntp().id)

    NTP.modify(ntp)

    assert len(root_node.children) == 1

    assert ntp() == root_node.children[0]
    assert ntp().parent == root_node
    assert ntp().name == old_name
    assert ntp().id == old_id
    assert ntp().terminal == old_terminal
    assert len(ntp().children) == 0

    # return to begin state
    del OBJECTS[ntp().name][ntp().id]
    del root_node.children[0]
    root_node.add(Node(NTP.name, terminal=False))

def test_ntp_delete(system_node):
    root_node = system_node

    ntp = NTP.create(root_node)

    NTP.delete(ntp)

    assert ntp() == None
    assert len(root_node.children) == 1
    assert root_node.children[0].parent == root_node
    assert root_node.children[0].name == 'NTP'
    assert root_node.children[0].terminal == False
    assert len(root_node.children[0].children) == 0
    assert not hasattr(root_node.children[0], 'id')


