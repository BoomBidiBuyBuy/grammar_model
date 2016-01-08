from model.model_fixtures import *
import pytest

@pytest.yield_fixture(scope="function")
def system_node():
    try:
        yield SYSTEM
    finally:
        while len(REP.list()):
            REP.list()[0]().delete()

def test_rep_create(system_node):
    assert len(REP.list()) == 0

    rep = REP.create(system_node)
    assert not rep() is None
    assert len(REP.list()) == 1
    assert rep().name == REP.name
    assert rep().parent.parent == system_node

    rep2 = REP.create(system_node)
    assert not rep2() is None
    assert len(REP.list()) == 2

def test_rep_modify(system_node):
    rep = REP.create(system_node)

    rep().modify(timeout=2.7)
    assert rep().timeout == 2.7

    rep().sync()

def test_rep_delete(system_node):
    REP.create(system_node)
    rep = REP.create(system_node)
    REP.create(system_node)

    assert len(REP.list()) == 3

    rep().delete()
    assert len(REP.list()) == 2

    REP.create(system_node)
    assert len(REP.list()) == 3