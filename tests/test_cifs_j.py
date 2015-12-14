from core.parser import *
import pytest
import os

@pytest.fixture(scope="module")
def config(request):
    path = os.path.dirname(__file__) + "\..\model\\"
    globals().update(load_model_file(path + "POOL.json"))
    globals().update(load_model_file(path + "NAS.json"))
    globals().update(load_model_file(path + "FI.json"))
    globals().update(load_model_file(path + "DNS.json"))
    globals().update(load_model_file(path + "NTP.json"))

    system_node = Node(name="*", terminal=False)
    system_node.add(Node(POOL.name, terminal=False))

    pool = POOL.create(system_node)
    nas = NAS.create(pool)

    def finalizer():
        while len(CIFS_J.list()):
            CIFS_J.delete(CIFS_J.list()[0])

        while len(DNS.list()):
            DNS.delete(DNS.list()[0])

        while len(FI.list()):
            FI.delete(FI.list()[0])

        while len(NAS.list()):
            NAS.delete(NAS.list()[0])

        while len(POOL.list()):
            POOL.delete(POOL.list()[0])

    request.addfinalizer(finalizer)

    return [nas, pool, system_node]

def is_cifs_existed(nas):
    return len([child for child in nas().children if child.name == CIFS_J.name and child.terminal]) > 0