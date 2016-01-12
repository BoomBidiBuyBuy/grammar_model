from common import *
from core.timer import Timer

def t_ldap_simple():
    nas = getNasServer()
    getInterface(nas)

    deleteNasInstances( nas, [NFS, LDAP, KERBEROS, CIFS, NIS, DNS])

    nas().modify(currectUnixDirectoryService = "NONE")

    ldap = getLdap(nas, use_ssl = False, portNumber = 388)

    ldap().modify( portNumber = 389 )
    ldap().modify( serverAddresses = ['1.2.3.4'] )
    ldap().modify( serverAddresses = [''] )
    ldap().modify( protocol = "LDAPS", verifyServerCertificate = False )

    assert ldap().portNumber == 389

    ldap().modify( authenticationType = "Anonymous" )
    ldap().modify( protocol = "LDAP" )
    ldap().modify( authenticationType = "Simple",
                  bindDN = "ab.cd.ef.g",
                  bindPassword = "Pass123!",
                  protocol = "LDAPS",
                  portNumber = 389,
                  verifyServerCertificate = False )
    ldap().modify( protocol = "LDAP", portNumber = 636 )
    ldap().modify( protocol = "LDAPS", verifyServerCertificate = False )

    assert ldap().portNumber == 636

    ldap().modify( protocol = "LDAP",
                 portNumber = 636,
                 profileDNS = "ou=profile,cn=default,dc=dvtfrance,dc=emc" )

    ldap().modify( authority = "DC=ldap-testing,DC=non-existing-rdn,DC=emc,DC=com", profileDNS = "" )
    ldap().modify( authority = "dc =  ABC  ,  cn  =  Test, ou =  Home Computers" )
    ldap().modify( authority = "spb.sspg.emc.com" )
    # Invalid port
    ldap().modify( portNumber = 0, is_error = True )

def t_ldap_kerberos_credentials():
    nas = getNasServer()
    deleteNasInstances(nas, [LDAP])

    getDns(nas)
    getKerberos(nas)

    for _ in range(6):
        LDAP.create(nas, principal = "", is_error = True)

def t_ldap_kerberos():
    nas = getNasServer()
    getInterface(nas)

    deleteNasInstances( nas, [LDAP, NFS, KERBEROS, CIFS, DNS])

    # no authentication type
    LDAP.create(nas, is_error = True)

    # KERBEROS doesn't exist
    LDAP.create(nas, authenticationType = "Kerberos",
                    is_error = True)

    getInterface( nas )
    dns = getDns( nas )
    kerberos = getKerberos( nas, realm = "abc.def")

    # realm are not equal
    LDAP.create(nas, authenticationType = "Kerberos",
                    isCifsAccountUsed = False,
                    is_error = True)

    KERBEROS.modify( kerberos, realm = "a.b.c.def")
    ldap = getLdap( nas, authenticationType = "Kerberos",
                        isCifsAccountUsed = False)

    ldap().modify( realm = "a.b.c.def" )

    assert ldap().realm == kerberos().realm

    # is used by ldap
    kerberos().delete( is_error = True )

    kerberos().modify( realm = "TEST.REALM.COM" )
    LDAP.list()

    ldap().modify( principal = "test-principal", password = "test-password")

    # realm is not equal to KERBEROS realm
    ldap().modify( realm = "test-ream", is_error = True )

    ldap().modify( password = "test-password" )

    cifs = getCifsServer( nas )

    kerberos().modify( realm = "TEST2.REALM.COM" )

    LDAP.list()

    ldap().modify( isCifsAccountUsed = True )
    # principal isn't specified
    ldap().modify( isCifsAccountUsef = False, is_error = True)

    # cifs used by ldap
    cifs().delete(is_error = True)

    # DNS destroy used by ldap kerberos
    dns().delete(is_error = True)

    ldap().delete()
    cifs().delete()
    kerberos().delete()
    dns().delete()

def t_ldap_kerberos_use_cifs():
    nas = getNasServer()
    getInterface(nas)

    deleteNasInstances( nas, [LDAP, FS])

    getInterface(nas)
    getDns(nas)
    getStandaloneCifsServer(nas)

    # no CIFS_J
    LDAP.create(nas, authenticationType = "Kerberos",
                    isCifsAccountUsed = True,
                    is_error = True)

    cifs = getCifsServer( nas )

    ldap = LDAP.create(nas, authenticationType = "Kerberos", isCifsAccountUsed = True)

    # CIFS used by ldap
    CIFS_SA.create(nas, is_error = True)
    # CIFS used by ldap
    cifs().delete(is_error = True)

    ldap().modify( isCifsAccountUsed = False,
                    principal = 'administrator',
                    password = "Password123!",
                    realm = 'a.b.c.def')

    # CIFS used by ldap
    CIFS_SA.create(nas, is_error = True)
    # CIFS used by ldap
    cifs().delete(is_error = True)

    ldap().delete()
    cifs().delete()

def t_ldap_cifs_using_other_account():
    nas = getNasServer()
    getInterface(nas)

    deleteNasInstances( nas, [LDAP, KERBEROS, DNS])

    # no KERBEROS
    LDAP.create( nas, authenticationType = "Kerberos",
                    isCifsAccountUsed = False,
                    realm = "a.b.c.def",
                    is_error = True)

    dns = getDns(nas)
    cifs = getCifsServer(nas)
    ldap = getLdap( nas, authenticationType = "Kerberos",
                        isCifsAccountUsed = False,
                        realm = 'a.b.c.def')
    kerberos = getKerberos(nas)

    kerberos().delete()
    ldap().delete()
    cifs().delete()
    dns().delete()

def t_ldap_auto_switch():
    nas = getNasServer()
    getInterface(nas)

    nas().modify( currentUnixDirectoryService = "NONE")

    deleteNasInstances( nas, [LDAP])

    ldap = getLdap(nas)
    NAS.list()

    ldap().delete()
    NAS.list()

    nas().modify( currentUnixDirectoryService = "NIS")

    ldap = getLdap(nas)
    NAS.list()

    ldap().delete()
    NAS.list()

def t_ldap_dep_errors():
    nas = getNasServer()
    getInterface(nas)

    ldap = getLdap(nas)
    ldap().modify(authority = 'DC=ldap-testing,DC=emc,DC=com')
    ldap().modify(is_error = True)

    # only one LDAP per NAS
    LDAP.create(nas, is_error = True)

    ldap().delete()
    deleteNasInstances( nas, [FI])

    # no interfaces
    getLdap(nas, is_error = True)

def t_ldap_basedn():
    nas = getNasServer()
    getInterface(nas)

    deleteNasInstances( nas, [LDAP])

    ldap = getLdap(nas)

    for _ in range(2):
        getLdap(nas, is_error = True)

    for _ in range(13):
        ldap().modify( is_error = True)

    for _ in range(9):
        ldap().modify()

def t_ldap_profiledn():
    nas = getNasServer()
    getInterface(nas)

    ldap = getLdap(nas)

    for _ in range(16):
        ldap().modify( is_error = True)

    for _ in range(9):
        ldap().modify()

def t_ldap_binddn():
    nas = getNasServer()
    getInterface(nas)
    deleteNasInstances( nas, [LDAP])

    for _ in range(15):
        getLdap(nas, is_error = True)

    ldap = getLdap(nas)

    for _ in range(8):
        ldap().modify()

    for _ in range(3):
        ldap().modify( is_error = True)

def t_ldap_bind_password():
    nas = getNasServer()
    getInterface(nas)
    deleteNasInstances( nas, [LDAP])

    for _ in range(3):
        getLdap(nas, is_error = True)

    ldap = getLdap(nas)

    ldap().modify()

def t_ldap_ip_addresses():
    nas = getNasServer()
    getInterface(nas)

    ldap = getLdap( nas )

    for _ in range(7):
        ldap().modify(is_error = True)

    ldap().modify()

def t_ldap_warnings():
    nas = getNasServer()
    deleteNasInstances(nas, [LDAP])

    nas().modify( currentUnixDirectoryService = "NONE")

    getInterface(nas)
    getDns(nas)
    getCifsServer(nas)
    getNfs(nas)

    # dir service ldap not exist
    nas().modify( isMultiProtocolEnabled = True,
                  currentUnixDirectoryService = 'LDAP',
                  is_error = True)

    ldap = getLdap( nas )
    nas().modify( isMultiProtocolEnabled = True )

    ldap().modify( is_error = True)
    ldap().modify( is_error = True)

    getNis(nas)

    # unsafe modify
    nas().modify( is_error = True)

    # destroy used by mp
    ldap().delete( is_error = True)

    nas().modify( isMultiProtocolEnabled = False)

def t_ldap_download_upload_conf():
    nas = getNasServer()
    getInterface(nas)
    getDns(nas)

    nas().download()
    nas().upload()
    nas().download()
    nas().upload()
    nas().download()

    [nas().upload(is_error = True) for _ in range(4)]

def t_ldap_download_upload_cacert():
    nas = getNasServer()
    getInterface(nas)
    ldap = getLdap(nas, protocol = "LDAPS", verifyServerCertificate = False)

    ldap().modify(is_error = True, verifyServerCertificate = True)

    nas().download()
    nas().upload(is_error = True)
    nas().upload(is_error = True)
    nas().upload()
    nas().download()
    nas().upload()

    ldap().modify( verifyServerCertificate = True )
    ldap().modify( verifyServerCertificate = False )

    ldap().modify( is_error = True, verifyServerCertificate = True )

def t_ldap_upload_content_cacert():
    nas = getNasServer()
    getInterface(nas)
    ldap = getLdap(nas, protocol = "LDAPS", verifyServerCertificate = False)

    nas().upload()

if __name__ == '__main__':
    NTP.create(SYSTEM)
    Timer.enable()
    t_ldap_simple()
    t_ldap_kerberos_credentials()
    t_ldap_kerberos()
    t_ldap_kerberos_use_cifs()
    t_ldap_cifs_using_other_account()
    t_ldap_auto_switch()
    t_ldap_dep_errors()
    t_ldap_basedn()
    t_ldap_profiledn()
    t_ldap_binddn()
    t_ldap_bind_password()
    t_ldap_ip_addresses()
    t_ldap_warnings()
    t_ldap_download_upload_conf()
    t_ldap_download_upload_cacert()
    t_ldap_upload_content_cacert()
    print(Timer.time())
