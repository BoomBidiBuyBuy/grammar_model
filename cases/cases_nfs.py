from common import *
from core.timer import Timer

def t_nfs_enable():
    nas = getNasServer()
    nfs = getNfs(nas)

    assert not nas() is None
    assert not nfs() is None
    assert nfs().parent == nas()

    nfs().modify( nfsv4Enabled = True,
                    isExtendedCredentialsEnaled = True,
                    credentialsCacheTTL = "00:05:00.000")
    assert nfs().nfsv4Enabled
    assert nfs().isExtendedCredentialsEnaled

    nfs().modify( nfsv4Enabled = False,
                    isExtendedCredentialsEnabled = False,
                    credentialsCacheTTL = "00:15:00.000")
    assert not nfs().nfsv4Enabled
    assert not nfs().isExtendedCredentialsEnabled

    nfs().modify( nfsv4Enaled = False )
    assert not nfs().nfsv4Enabled

    nfs().delete()
    assert nfs() is None

def t_nfs_secure():
    nas = getNasServer()
    assert deleteNasInstances( nas, [NFS, KERBEROS])
    assert getInterface(nas)
    assert getDns(nas)
    assert getNis(nas)

    cifs = getCifsServer(nas)
    assert cifs().type == CIFS_J.name

    nas().modify( currentUnixDirectoryService = "NIS")

    nfs = getNfs(nas, isSecureEnaled = True)

    nfs().modify( is_error = True )
    nfs().modify( hostName = "some_name" )
    nfs().modify( is_error = True )
    nfs = getNfs(nas, isSecureEnabled = False)
    nfs().modify( is_error = True)
    nfs = getNfs(nas, isSecureEnabled = True)
    cifs().modify()

    CIFS.list()
    NFS.list()

    nfs().modify( is_error = True )
    nfs().modify( is_error = True )
    nfs = getNfs( nas, isSecureEnabled = False )

    cifs().delete()

    nfs().delete()

def t_nfs_secure_win_kdc_deps():
    nas = getNasServer()
    deleteNasInstances(nas, [NFS, CIFS, FI, LDAP, NIS])

    getDns(nas)

    [getNfs(nas, isSecureEnabled = True, is_error = True) for _ in range(4)]
    getInterface(nas)
    nis = getNis(nas)
    getStandaloneCifsServer(nas)
    getCifsServer(nas)

    getNfs(nas, isSecureEnabled = True, is_error = True)
    getNfs(nas, isSecureEnabled = True, is_error = True)

    nfs = getNfs(nas, isSecureEnabled = True,
                    kdcType = "Windows")

    cifs = [cifs for cifs in CIFS.list()][0]
    nfs().modify( isSecureEnabled = True, is_error = True)
    nfs().delete( is_error = True )
    nfs().modify( isSecureEnabled = False, is_error = True )

    nfs().modify( isSecureEnabled = False )
    nfs().modify( isSecureEnabled = True,
                    kdcType = "Windows")

    nfs().delete( is_error = True)
    nfs().delete()

    nfs = getNfs( nas, isSecureEnabled = True)
    deleteNasInstances(nas, [FI])
    nfs().modify( isSecureEnabled = False, is_error = True)
    nfs().delete( is_error = True)

    getInterface( nas )

    cifs().modify( is_error = True)
    cifs().delete( is_error = True)
    nas().modify( is_error = True)
    nis().delete( is_error = True)

    ldap = getLdap(nas)
    nas().modify( currentUnixDirectoryService = "LDAP")
    nis().delete()

    ldap().delete( is_error = True )
    nfs().modify( isSecureEnabled = False)

    deleteNasInstances(nas, [NIS, LDAP, CIFS, FI])

    [getNfs(nas, isSecureEnabled = True, is_error = True) for _ in range(4)]
    getInterface(nas)
    getNis(nas)
    getStandaloneCifsServer(nas)
    getCifsServer(nas)
    nfs = getNfs(nas)

    nfs().modify( isSecureEnabled = True )
    nfs().modify( isSecureEnabled = False )

def t_nfs_secure_custom_kdc_deps():
    nas = getNasServer()

    deleteNasInstances( nas, [NFS, LDAP, KERBEROS, NIS, NFS])

    dns = getDns( nas )

if __name__ == '__main__':
    Timer.enable()
    t_nfs_enable()
    t_nfs_secure()
    t_nfs_secure_win_kdc_deps()
    t_nfs_secure_custom_kdc_deps()
    print(Timer.time())