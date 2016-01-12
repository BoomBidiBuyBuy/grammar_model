from common import *
from core.timer import Timer

def t_cifs_share_on_filesystem():
    nas = getNasServer()
    getNfs(nas)
    getInterface(nas)

    cifs = getAnyCifsServer(nas)

    fs = getCifsFilesystem(nas)
    cleanUpFilesystem(fs)

    sh = SH_CIFS.create(fs)
    sh().modify()

    SH_CIFS.list()
    sh().delete()

    SH_CIFS.create(fs)

def t_cifs_share_on_filesystem_implicit_delete():
    nas = getNasServer()
    cifs = getAnyCifsServer(nas)
    fs = getCifsFilesystem(nas)
    cleanUpFilesystem(fs)

    sh = SH_CIFS.create(fs)
    fs().delete()
    assert sh() is None

def t_cifs_share_on_snapshot():
    nas = getNasServer()

    nfs = getNfs(nas)
    assert not nfs() is None
    fi = getInterface(nas)
    assert not fi() is None

    cifs = getAnyCifsServer(nas)
    assert not cifs() is None
    fs = getCifsFilesystem(nas)
    assert not fs() is None
    snap = SNAP_CIFS.create(fs)
    assert not snap() is None

    sh = SH_CIFS.create(snap)
    assert not sh() is None
    sh().modify()
    sh().modify()
    sh().delete()
    assert sh() is None

def t_cifs_share_replication():
    getNasReplicationSession()
    nas_src = getNasServer()
    nas_dst = getNasServer(not_nas=nas_src)
    getAnyCifsServer(nas_src)
    getAnyCifsServer(nas_dst)

    fs_src = getCifsFilesystem(nas_src)
    fs_dst = getCifsFilesystem(nas_dst)

    sh = SH_CIFS.create(fs_src)

    # TODO: sync replication

    sh().delete()

    # TODO: sync replication

    snap = SNAP_CIFS.create( fs_dst )
    assert not snap() is None

def t_cifs_share_acl():
    nas = getNasServer()
    getNfs(nas)

    cifs = getAnyCifsServer(nas)
    fs = getCifsFilesystem(nas)
    cleanUpFilesystem(fs)

if __name__ == '__main__':
    Timer.enable()
    t_cifs_share_on_filesystem()
    t_cifs_share_on_filesystem_implicit_delete()
    t_cifs_share_replication()
    t_cifs_share_on_snapshot()
    print(Timer.time())
