from common import *
from core.timer import Timer

def t_nas_simple():
    nas = getNasServer()

    nas().modify( currentUnixDirectoryService = "NONE",
                    isExtendedUnixCredentialEnabled = True)
    assert nas().currentUnixDirectoryService == "NONE"
    assert nas().isExtendedUnixCredentialEnabled

    nas().modify( isExtendedUnixCredentialEnabled = False )
    assert not nas().isExtendedUnixCredentialEnabled

    nas().delete()
    assert nas() is None

def t_nas_change_sp():
    nas = getNasServer()
    nas().modify()

def t_nas_bulk_delete():
    nas = getNasServer()
    assert getInterface(nas)
    assert getDns(nas)
    assert getNis(nas)
    assert getLdap(nas)
    assert getNdmp(nas)
    assert getDhsm(nas)
    assert getNfs(nas)
    assert getStandaloneCifsServer(nas)
    assert getFtp(nas)
    assert getKerberos(nas)

    nas().delete()

    nas = getNasServer()
    getInterface(nas)
    getDns(nas)
    getCifsServer(nas)
    getNis(nas)
    NFS_WS.create(nas)

    nas().delete()

def t_nas_name():
    nas = getNasServer()
    nas().modify()

def t_nas_download_upload_locals():
    nas = getNasServer()
    nas().modify()

def t_nas_mp_users():
    nas = getNasServer(isMultiProtocolEnabled=True)
    deleteNasInstances(nas, [FS])

    [nas().modify() for _ in range(7)]

    deleteNasInstances(nas, [CIFS])

    nas().modify()

def t_nas_mp_standalone_cifs():
    nas = getNasServer(isMultiProtocolEnabled=True)
    deleteNasInstances(nas, [FS])

    nas().modify(isMultiProtocolEnabled = False)

    getStandaloneCifsServer(nas)
    getNfs(nas)
    getNis(nas)
    nas().modify(currentUnixDirectoryService = "NIS")

def t_nas_mp_with_fs():
    nas = getNasServer(isMultiProtocolEnasbled = True)

    nas().modify()
    nas().modify()
    nas().modify()
    getNfs(nas)
    getInterface(nas)
    getDns(nas)
    getCifsServer(nas)
    getCifsFilesystem(nas)
    nas().modify(isMultiProtocolEnabled=False)

    nas().delete()

def t_nas_mp_fs_remapping():
    nas = getNasServer()

    getInterface(nas)
    getDns(nas)
    getNis(nas)
    nas().modify(currentUnixDirectoryService="NIS")
    getNfs(nas)
    getCifsServer(nas)

    getCifsFilesystem(nas)
    getNfsFilesystem(nas)

    nas().modify(isMultiProtocolEnabled=True)

    deleteNasInstances(nas, [FS])
    nas().modify( isMultiProtocolEnabled=False)

def t_nas_mp_check_deps():
    nas = getNasServer()
    getInterface(nas)
    deleteNasInstances(nas, [NFS, LDAP, KERBEROS, CIFS, DNS])
    nis = getNis(nas)
    getNfs(nas)
    dns = getDns(nas)
    getCifsServer(nas)
    dns().modify()
    dns().modify()
    nis().modify()
    nis().delete()
    ldap = getLdap(nas)
    ldap().modify()
    ldap().delete()

def t_nas_mapping_report():
    nas = getNasServer()
    deleteNasInstances(nas, [NFS, LDAP, NIS, KERBEROS, CIFS, DNS, FI])

    getInterface(nas)
    cifs = getStandaloneCifsServer(nas)
    getDns(nas)
    cifs().modify()
    nis = getNis(nas)
    nis().modify()
    nis().delete()
    ldap = getLdap(nas)
    ldap().modify()

def t_nas_no_dir_service_health():
    nas = getNasServer()
    deleteNasInstances(nas, [LDAP, CIFS, NIS, KERBEROS, DNS])
    nas().modify( currentUnixDirectoryService = "NONE")
    nas().modify( currentUnixDirectoryService = "LDAP")
    nas().modify( currentUnixDirectoryService = "NONE")
    nas().modify( currentUnixDirectoryService = "NIS")
    nas().modify( currentUnixDirectoryService = "NONE")

def t_nas_mp_health_ldap():
    nas = getNasServer(isMulriProtocolEnaled = True,
                        currentUnixDirectoryService="LDAP")
    getInterface(nas)
    getDns(nas)
    cifs = getCifsServer(nas)
    nfs = getNfs(nas)
    ldap = getLdap(nas)
    nfs().delete()
    cifs().delete()
    nas().modify(isMultiProtocolEnabled=False)
    ldap().delete()
    nas().delete()

def t_nas_mp_health_nis():
    nas = getNasServer(isMultiProtocolEnabled=True,
                        currentUnixDirectoryService = "NIS")

    getInterface(nas)
    getDns(nas)
    getCifsServer(nas)
    getNfs(nas)
    nis = getNis(nas)

    nas().modify( isMultiProtocolEnabled = False)
    nis().delete()
    nas().delete()

if __name__ == '__main__':
    Timer.enable()
    t_nas_simple()
    t_nas_change_sp()
    t_nas_bulk_delete()
    t_nas_name()
    t_nas_download_upload_locals()
    t_nas_mp_users()
    t_nas_mp_standalone_cifs()
    t_nas_mp_with_fs()
    t_nas_mp_fs_remapping()
    t_nas_mp_check_deps()
    t_nas_mapping_report()
    t_nas_no_dir_service_health()
    t_nas_no_dir_service_health()
    t_nas_mp_health_nis()
    print(Timer.time())