import pytest
import os
from core.parser import *

def load(name):
    return load_model_file(os.path.dirname(__file__) + "\..\model\\" + name)

@pytest.fixture(scope="session")
def ntp_type():
    return load("NTP.json")

@pytest.fixture(scope="session")
def pool_type():
    return load("POOL.json")

@pytest.fixture(scope="session")
def nas_type():
    return load("NAS.json")

@pytest.fixture(scope="session")
def fi_type():
    return load("FI.json")

@pytest.fixture(scope="session")
def dns_type():
    return load("DNS.json")

@pytest.fixture(scope="session")
def nis_type():
    return load("NIS.json")

@pytest.fixture(scope="session")
def ldap_type():
    return load("LDAP.json")

@pytest.fixture(scope="session")
def kerberos_type():
    return load("KERBEROS.json")

@pytest.fixture(scope="session")
def ndmp_type():
    return load("NDMP.json")

@pytest.fixture(scope="session")
def asa_type():
    return load("ASA.json")

@pytest.fixture(scope="session")
def cifs_j_type():
    return load("CIFS_J.json")

@pytest.fixture(scope="session")
def cifs_sa_type():
    return load("CIFS_SA.json")

@pytest.fixture(scope="session")
def nfs_cs_type():
    return load("NFS_CS.json")

@pytest.fixture(scope="session")
def nfs_ws_type():
    return load("NFS_WS.json")