from model.model_fixtures import load_all
from core.parser import Node

[globals().update(obj) for obj in load_all()]

system = Node(name="*", terminal=False)
system.add(Node(POOL.name, terminal=False))
system.add(Node(NTP.name, terminal=False))

globals().update({"SYSTEM" : system})

def getPool():
    pools = POOL.list()

    if len(pools):
        return pools[0]

    return POOL.create(SYSTEM)

def getNasServer(**kwargs):
    for nas in NAS.list(**kwargs):
        return nas

    return NAS.create(getPool(), **kwargs)

def deleteNasInstances(nas, types):
    for type in types:
        objects_for_deletion = []
        for object in type.list():
            if object().parent == nas():
                objects_for_deletion.append(object)

        for object in objects_for_deletion:
            type.delete(object)

def getSingleObject(nas, type):
    for object in type.list():
        if object().parent == nas():
            return object

    return type.create(nas)

def getDns(nas):
    return getSingleObject(nas, DNS)

def getFtp(nas):
    return getSingleObject(nas, FTP)

def getNdmp(nas):
    return getSingleObject(nas, NDMP)

def getDhsm(nas):
    return getSingleObject(nas, ASA)

def getNis(nas):
    return getSingleObject(nas, NIS)

def getLdap(nas):
    return getSingleObject(nas, LDAP)

def getKerberos(nas):
    return getSingleObject(nas, KERBEROS)

def getInterface(nas):
    for fi in FI.list():
        if fi().parent.parent == nas():
            return fi

    return FI.create(nas)

def getCifsServer(nas):
    for cifs in CIFS_J.list():
        if cifs().parent == nas():
            return cifs

    for cifs in CIFS_SA.list():
        if cifs().parent == nas():
            CIFS_SA.delete(cifs)
            return CIFS_J.create(nas)

    return CIFS_J.create(nas)

def getNfs(nas):
    for nfs in NFS_CS.list() + NFS_WS.list() + NFS.list():
        if nfs().parent == nas():
            return nfs

    return NFS.create(nas)

