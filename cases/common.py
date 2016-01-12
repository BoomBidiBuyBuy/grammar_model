from model.model_fixtures import load_all
from core.parser import Node
from core.parser import OBJECTS
from collections import defaultdict
import weakref

[globals().update(obj) for obj in load_all()]

system = Node(name="*", terminal=False)
system.add(Node(POOL.name, terminal=False))
system.add(Node(NTP.name, terminal=False))
NTP.create(system)

globals().update({"SYSTEM" : system})

def restore(pool):
    copy_pool = Node(other_node=pool)

    for inx in range(len(SYSTEM.children)):
        if SYSTEM.children[inx].name == POOL.name:
            SYSTEM.children[inx].children.append(copy_pool)
            copy_pool.parent = SYSTEM.children[inx]
            break

    global OBJECTS

    def restore_node(node):
        for child in node.children:
            if child.terminal:
                child.handle_id()
                n = weakref.ref(child)
                OBJECTS[child.name][child.id] = n

                if child.type != child.name:
                   OBJECTS[child.type][child.id] = n

            restore_node(child)

    copy_pool.handle_id()
    OBJECTS[POOL.name][copy_pool.id] = weakref.ref(copy_pool)

    # restore NTP
    for child in SYSTEM.children:
        if child.name == NTP.name:
            OBJECTS[NTP.name][child.id] = weakref.ref(child)
            break

    restore_node(copy_pool)

def clearAll():
    pool = POOL.list()[0]

    for inx in range(len(SYSTEM.children)):
        if SYSTEM.children[inx].name == POOL.name:
            SYSTEM.children[inx].children = []
            break

    global OBJECTS
    OBJECTS.clear()

    return pool

def getPool():
    pools = POOL.list()

    if len(pools):
        return pools[0]

    return POOL.create(SYSTEM)

def getNasObjects(nas, type, double_parent=False):
    if double_parent:
        return [obj for obj in type.list() if obj().parent.parent == nas()]

    return [obj for obj in type.list() if obj().parent == nas()]

def getNasServer(not_nas = None, **kwargs):
    for nas in NAS.list(**kwargs):
        if not_nas and nas() == not_nas():
            continue

        return nas

    return NAS.create(getPool(), **kwargs)

def cleanUpSnapshot(snap):
    [share().delete() for share in SH.list()
        if share().parent.parent == snap()]

def cleanUpFilesystem(fs):
    [share().delete() for share in SH.list()
        if share().parent.parent == fs()]
    [cleanUpSnapshot(snap) for snap in SNAP.list()
        if snap().parent.parent == fs()]

def cleanUpNasFilesystems(nas):
    for fs in FS.list():
        if fs().parent.parent == nas():
            cleanUpFilesystem(fs)

def deleteNasInstances(nas, types):
    for type in types:
        objects_for_deletion = []
        for object in type.list():
            if object().parent == nas():
                objects_for_deletion.append(object)

        for object in objects_for_deletion:
            if object().name == CIFS.name:
                cleanUpNasFilesystems(nas)

                if object().type == CIFS_J.name:
                    getInterface(nas)
                    getDns(nas)
            if object().name == NFS.name:
                cleanUpNasFilesystems(nas)
                if object().type != NFS.name:
                    getInterface(nas)
            if object().name == FS.name:
                cleanUpFilesystem(object)
            if object().name == LDAP.name:
                getInterface(nas)
                nfs = getNasObjects(nas, NFS)

                if len(nfs):
                    nfs = nfs[0]

                    if nfs().type == NFS_CS.name:
                        getKerberos(nas)
                        getNis(nas)
                    if nfs().type == NFS_WS.name:
                        getCifsServer(nas)
                        getNis(nas)

                    nfs().delete()


            object().delete()

            # checking
            if not object() is None:
                object().delete()

def getSingleObject(nas, type, **kwargs):
    for object in type.list():
        if object().parent == nas():
            for key, value in kwargs.items():
                if not hasattr(object(), key) or \
                        getattr(object(), key) != value:
                    object().modify(**kwargs)

            return object

    return type.create(nas, **kwargs)

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

def getLdap(nas, **kwargs):
    return getSingleObject(nas, LDAP, **kwargs)

def getKerberos(nas, **kwargs):
    return getSingleObject(nas, KERBEROS, **kwargs)

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

def getAnyCifsServer(nas, **kw):
    for cifs in CIFS.list():
        if cifs().parent == nas():
            return cifs

    return getStandaloneCifsServer(nas)

def getNasReplicationSession():
    # TODO
    pass


def getStandaloneCifsServer(nas):
    for cifs in CIFS_J.list():
        if cifs().parent == nas():
            cifs().delete()

    for cifs in CIFS_SA.list():
        if cifs().parent == nas():
            return cifs

    return CIFS_SA.create(nas)

def getNfsIfExists(nas):
    for nfs in NFS.list():
        if nfs().parent == nas():
            return nfs
    return None

def getCifsIfExists(nas):
    for cifs in CIFS_J.list():
        if cifs().parent == nas():
            return cifs
    return None

def getNfs(nas, **kwargs):
    if 'isSecureEnabled' in kwargs:
        if kwargs['isSecureEnabled']:
            nfs = getNfsIfExists(nas)

            if nfs:
                if nfs().type != NFS.name:
                    return nfs
                else:
                    nfs().delete()

            if getCifsIfExists(nas):
                return NFS_WS.create(nas, **kwargs)
            else:
                return NFS_CS.create(nas, **kwargs)
        else:
            nfs = getNfsIfExists(nas)

            if nfs:
                if nfs().type == NFS_CS.name or nfs().type == NFS_WS.name:
                    nfs().delete()
                else:
                    return nfs

            return NFS.create(nas, **kwargs)

    return getSingleObject(nas, NFS, **kwargs)

def getCifsFilesystem(nas, **kw):
    return getSingleObject(nas, FS_CIFS, **kw)

def getNfsFilesystem(nas, **kw):
    return getSingleObject(nas, FS_NFS, **kw)

def cleanUpFilesystem(fs):
    for_deletion = [sh for sh in SH.list() if sh().parent.parent == fs()]
    [sh().delete() for sh in for_deletion]
