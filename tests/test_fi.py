from model.model_fixtures import *
import pytest

@pytest.yield_fixture(scope="function")
def nas_nodes(nas, pool):
    try:
        yield [nas, NAS.create(pool), SYSTEM]
    finally:
        pool().delete()

def check_interface(interface):
    assert interface().name == FI.name
    assert interface().terminal == True
    assert hasattr(interface(), 'id')
    assert interface in FI.list()

    return interface

def find_nterm(nas):
    for child in nas().children:
        if child.name == FI.name:
            return child

def test_fi_create(nas_nodes):
    nas = nas_nodes[0]

    # find terminal
    fi_term = None
    for child in nas().children:
        if child.name == FI.name:
            fi_term = child
            break

    assert not fi_term is None

    assert len(fi_term.children) == 0
    assert fi_term.name == FI.name
    assert fi_term.terminal == False
    assert not hasattr(fi_term, 'id')
    assert len(FI.list()) == 0

    fi1 = FI.create(nas)

    assert len(fi_term.children) == 1
    assert len(FI.list()) == 1

    check_interface(fi1)

    fi2 = FI.create(nas)

    assert len(fi_term.children) == 2
    assert len(FI.list()) == 2

    check_interface(fi2)

    fi3 = FI.create(nas)

    assert len(fi_term.children) == 3
    assert len(FI.list()) == 3

    check_interface(fi3)

    # return to the start state
    FI.delete(fi1)
    FI.delete(fi2)
    FI.delete(fi3)
    assert len(FI.list()) == 0

def test_fi_create2(nas_nodes):
    nas1, nas2 = nas_nodes[0], nas_nodes[1]

    assert len(FI.list()) == 0

    fi_nterm1, fi_nterm2 = find_nterm(nas1), find_nterm(nas2)

    assert not fi_nterm1 is None
    assert not fi_nterm2 is None

    fi1 = check_interface(FI.create(nas1))
    fi2 = check_interface(FI.create(nas1))
    fi3 = check_interface(FI.create(nas1))

    fi4 = check_interface(FI.create(nas2))
    fi5 = check_interface(FI.create(nas2))

    assert len(FI.list()) == 5
    assert len(fi_nterm1.children) == 3
    assert len(fi_nterm2.children) == 2

    # return to the begin state
    while len(fi_nterm1.children):
        fi = fi_nterm1.children[0]
        FI.delete(fi)

    while len(fi_nterm2.children):
        fi = fi_nterm2.children[0]
        FI.delete(fi)

    assert len(FI.list()) == 0

def test_fi_modify(nas_nodes):
    nas = nas_nodes[0]

    fi = FI.create(nas)

    check_interface(fi)

    FI.modify(fi)

    check_interface(fi)

    fi().addresses = ["1.2.3.4"]

    FI.delete(fi)

    assert len(FI.list()) == 0

def test_fi_delete(nas_nodes):
    nas1, nas2 = nas_nodes[0], nas_nodes[1]

    fi_nterm1, fi_nterm2 = find_nterm(nas1), find_nterm(nas2)

    assert not fi_nterm1 is None
    assert not fi_nterm2 is None

    fi1, fi2, fi3 = FI.create(nas1), FI.create(nas1), FI.create(nas1)
    fi4, fi5 = FI.create(nas2), FI.create(nas2)

    assert len(fi_nterm1.children) == 3
    assert len(fi_nterm2.children) == 2
    assert len(FI.list()) == 5

    FI.delete(fi1)

    assert len(fi_nterm1.children) == 2
    assert len(fi_nterm2.children) == 2
    assert len(FI.list()) == 4
    assert fi1() is None

    FI.delete(fi2)

    assert len(fi_nterm1.children) == 1
    assert len(fi_nterm2.children) == 2
    assert len(FI.list()) == 3
    assert fi2() is None

    FI.delete(fi3)

    assert len(fi_nterm1.children) == 0
    assert len(fi_nterm2.children) == 2
    assert len(FI.list()) == 2
    assert fi3() is None

    FI.delete(fi4)

    assert len(fi_nterm1.children) == 0
    assert len(fi_nterm2.children) == 1
    assert len(FI.list()) == 1
    assert fi4() is None

    FI.delete(fi5)

    assert len(fi_nterm1.children) == 0
    assert len(fi_nterm2.children) == 0
    assert len(FI.list()) == 0
    assert fi5() is None

def test_fi_delete_nas(nas_nodes):
    nas1, nas2 = nas_nodes[0], nas_nodes[1]

    fi_nterm2 = find_nterm(nas2)

    for _ in range(5):
        FI.create(nas1)

    for _ in range(7):
        FI.create(nas2)

    assert len(FI.list()) == 12

    NAS.delete(nas1)

    assert len(FI.list()) == 7
    assert len(fi_nterm2.children) == 7

    NAS.delete(nas2)

    assert len(FI.list()) == 0




