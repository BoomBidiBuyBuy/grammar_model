from core.parser import *
import pytest
import os

@pytest.fixture(scope="module")
def config(request):
    path = os.path.dirname(__file__) + "\..\model\\"
    globals().update(load_model_file(path + "POOL.json"))
    globals().update(load_model_file(path + "NAS.json"))
    globals().update(load_model_file(path + "DNS.json"))

    system_node = Node(name="*", terminal=False)
    system_node.add(Node(POOL.name, terminal=False))

    pool = POOL.create(system_node)
    nas = NAS.create(pool)

    def finalizer():
        while len(DNS.list()):
            DNS.delete(DNS.list()[0])

        while len(NAS.list()):
            NAS.delete(NAS.list()[0])

        while len(POOL.list()):
            POOL.delete(POOL.list()[0])

    request.addfinalizer(finalizer)

    return [nas, pool, system_node]

def is_dns_existed(nas):
    return len([child for child in nas().children if child.name == DNS.name and child.terminal]) > 0

def test_dns_create(config):
    nas = config[0]

    assert len(DNS.list()) == 0
    assert not is_dns_existed(nas)

    dns = DNS.create(nas)

    assert len(DNS.list()) == 1
    assert dns().name == DNS.name
    assert dns().terminal
    assert hasattr(dns(), 'id')
    assert dns().parent == nas()
    assert is_dns_existed(nas)

    DNS.create(nas)

    assert len(DNS.list()) == 1

    # tear down
    DNS.delete(dns)

def test_dns_modify(config):
    nas = config[0]

    assert len(DNS.list()) == 0
    assert not is_dns_existed(nas)

    dns = DNS.create(nas)

    DNS.modify(dns)

    assert is_dns_existed(nas)
    assert len(DNS.list()) == 1
    assert dns().name == DNS.name
    assert dns().terminal
    assert hasattr(dns(), 'id')
    assert dns().parent == nas()

    # tear down
    DNS.delete(dns)

def test_dns_delete(config):
    nas1, pool, _ = config
    nas2 = NAS.create(pool)
    nas3 = NAS.create(pool)

    dns1 = DNS.create(nas1)

    assert dns1().parent == nas1()
    assert is_dns_existed(nas1)
    assert not is_dns_existed(nas2)
    assert not is_dns_existed(nas3)
    assert len(DNS.list()) == 1

    dns3 = DNS.create(nas3)

    assert dns3().parent == nas3()
    assert is_dns_existed(nas1)
    assert not is_dns_existed(nas2)
    assert is_dns_existed(nas3)
    assert len(DNS.list()) == 2

    dns2 = DNS.create(nas2)

    assert dns2().parent == nas2()
    assert is_dns_existed(nas1)
    assert is_dns_existed(nas2)
    assert is_dns_existed(nas3)
    assert len(DNS.list()) == 3

    DNS.delete(dns1)

    assert dns1() == None
    assert not is_dns_existed(nas1)
    assert len(DNS.list()) == 2

    dns1 = DNS.create(nas1)

    assert dns1().parent == nas1()
    assert is_dns_existed(nas1)
    assert len(DNS.list()) == 3

    DNS.delete(dns1)
    DNS.delete(dns2)
    DNS.delete(dns3)

    assert dns1() == None
    assert dns2() == None
    assert dns3() == None
    assert len(DNS.list()) == 0