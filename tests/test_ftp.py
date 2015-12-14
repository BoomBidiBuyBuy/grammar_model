from core.parser import *
import pytest
import os

@pytest.fixture(scope="module")
def config(request):
    path = os.path.dirname(__file__) + "\..\model\\"
    globals().update(load_model_file(path + "POOL.json"))
    globals().update(load_model_file(path + "NAS.json"))
    globals().update(load_model_file(path + "FTP.json"))

    system_node = Node(name="*", terminal=False)
    system_node.add(Node(POOL.name, terminal=False))

    pool = POOL.create(system_node)
    nas = NAS.create(pool)

    def finalizer():
        while len(FTP.list()):
            FTP.delete(FTP.list()[0])

        while len(NAS.list()):
            NAS.delete(NAS.list()[0])

        while len(POOL.list()):
            POOL.delete(POOL.list()[0])

    request.addfinalizer(finalizer)

    return [nas, pool, system_node]

def is_ftp_existed(nas):
    return len([child for child in nas().children if child.name == FTP.name and child.terminal]) > 0

def test_ftp_create(config):
    nas = config[0]

    assert len(FTP.list()) == 0
    assert not is_ftp_existed(nas)

    ftp = FTP.create(nas)

    assert len(FTP.list()) == 1
    assert ftp().name == FTP.name
    assert ftp().terminal
    assert hasattr(ftp(), 'id')
    assert ftp().parent == nas()
    assert is_ftp_existed(nas)

    FTP.create(nas)

    assert len(FTP.list()) == 1

    # tear down
    FTP.delete(ftp)

def test_ftp_modify(config):
    nas = config[0]

    assert len(FTP.list()) == 0
    assert not is_ftp_existed(nas)

    ftp = FTP.create(nas)

    FTP.modify(ftp)

    assert is_ftp_existed(nas)
    assert len(FTP.list()) == 1
    assert ftp().name == FTP.name
    assert ftp().terminal
    assert hasattr(ftp(), 'id')
    assert ftp().parent == nas()

    # tear down
    FTP.delete(ftp)

def test_ftp_delete(config):
    nas1, pool, _ = config
    nas2 = NAS.create(pool)
    nas3 = NAS.create(pool)

    ftp1 = FTP.create(nas1)

    assert ftp1().parent == nas1()
    assert is_ftp_existed(nas1)
    assert not is_ftp_existed(nas2)
    assert not is_ftp_existed(nas3)
    assert len(FTP.list()) == 1

    ftp3 = FTP.create(nas3)

    assert ftp3().parent == nas3()
    assert is_ftp_existed(nas1)
    assert not is_ftp_existed(nas2)
    assert is_ftp_existed(nas3)
    assert len(FTP.list()) == 2

    ftp2 = FTP.create(nas2)

    assert ftp2().parent == nas2()
    assert is_ftp_existed(nas1)
    assert is_ftp_existed(nas2)
    assert is_ftp_existed(nas3)
    assert len(FTP.list()) == 3

    FTP.delete(ftp1)

    assert ftp1() == None
    assert not is_ftp_existed(nas1)
    assert len(FTP.list()) == 2

    ftp1 = FTP.create(nas1)

    assert ftp1().parent == nas1()
    assert is_ftp_existed(nas1)
    assert len(FTP.list()) == 3

    FTP.delete(ftp1)
    FTP.delete(ftp2)
    FTP.delete(ftp3)

    assert ftp1() == None
    assert ftp2() == None
    assert ftp3() == None
    assert len(FTP.list()) == 0