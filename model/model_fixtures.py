import os

import pytest

from core.parser import *

def load(name):
    return load_model_file(os.path.dirname(__file__) + "\..\model\\" + name)

def load_all():
    result = []
    result.append(load("NTP.json"))
    result.append(load("POOL.json"))
    result.append(load("NAS.json"))
    result.append(load("FI.json"))
    result.append(load("FTP.json"))
    result.append(load("DNS.json"))
    result.append(load("NIS.json"))
    result.append(load("LDAP.json"))
    result.append(load("KERBEROS.json"))
    result.append(load("NDMP.json"))
    result.append(load("ASA.json"))
    result.append(load("CIFS.json"))
    result.append(load("CIFS_J.json"))
    result.append(load("CIFS_SA.json"))
    result.append(load("NFS_CS.json"))
    result.append(load("NFS_WS.json"))
    result.append(load("NFS.json"))
    result.append(load("FS.json"))
    result.append(load("FS_CIFS.json"))
    result.append(load("FS_NFS.json"))
    result.append(load("FS_MUP.json"))
    result.append(load("SH_NFS.json"))
    result.append(load("SH_CIFS.json"))
    result.append(load("SNAP_NFS.json"))
    result.append(load("SNAP_CIFS.json"))
    result.append(load("SNAP_MUP.json"))
    result.append(load("HOST.json"))
    result.append(load("REP.json"))

    return result

[globals().update(obj) for obj in load_all()]

system = Node(name="*", terminal=False)
system.add(Node(POOL.name, terminal=False))
system.add(Node(NTP.name, terminal=False))
system.add(Node(REP.name, terminal=False))

globals().update({"SYSTEM": system})

@pytest.fixture(scope="function")
def pool():
    for pool in POOL.list():
        return pool

    return POOL.create(SYSTEM)

@pytest.fixture(scope="function")
def ntp():
    return NTP.create(SYSTEM)

@pytest.fixture(scope="function")
def nas(pool):
    return NAS.create(pool)

@pytest.fixture(scope="function")
def fi(nas):
    return FI.create(nas)

@pytest.fixture(scope="function")
def dns(nas):
    return DNS.create(nas)
