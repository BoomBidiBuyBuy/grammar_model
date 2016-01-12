from common import *
from core.timer import Timer

def t_nfs_ahare_filesystem():
    nas = getNasServer()
    getInterface(nas)
    nfs = getNfs(nas)
    cifs = getAnyCifsServer(nas)
    fs = getNfsFilesystem(nas)
    cleanUpFilesystem(fs)

    sh = SH_NFS.create(fs)
    sh().modify()
    sh().delete()

def t_nfs_share_on_filesystem_implicit_delete():
    nas = getNasServer()
    nfs = getNfs(nas)
    fs = getNfsFilesystem(nas)
    cleanUpFilesystem(fs)

    sh = SH_NFS.create(fs)
    sh().delete()

def t_nfs_share_on_snapshot():
    nas = getNasServer()
    getInterface(nas)
    getAnyCifsServer(nas)
    nfs = getNfs(nas)
    fs = getNfsFilesystem(nas)
    snap = SNAP_NFS.create(fs)
    cleanUpFilesystem(snap)

    sh = SH_NFS.create(snap)
    sh().modify()
    sh().modify()
    sh().modify()
    sh().delete()

def t_nfs_share_on_snapshot_implicit_delete():
    nas = getNasServer()
    nfs = getNfs(nas)
    fs = getNfsFilesystem(nas)
    snap = SNAP_NFS.create(fs)
    cleanUpFilesystem(snap)

    sh = SH_NFS.create(snap)
    sh().delete()

if __name__ == '__main__':
    Timer.enable()
    t_nfs_ahare_filesystem()
    t_nfs_share_on_filesystem_implicit_delete()
    t_nfs_share_on_snapshot()
    t_nfs_share_on_snapshot_implicit_delete()
    print(Timer.time())