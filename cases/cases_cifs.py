from common import *
from core.timer import Timer

def t_cifs_domain():
    nas = getNasServer()
    dns = getDns(nas)

    interfaces = [fi for fi in FI.list() if fi().parent == nas()]
    for interface in interfaces[:-1]:
        interface().delete()

    interface = getInterface( nas )
    cifs = getCifsServer( nas )
    cifs().delete()

    Timer.add(30.0)

    cifs = getCifsServer(nas)
    interface().modify()
    cifs().modify()

    # with ethernet ports
    interface().modify()
    cifs().modify()

    # CIFS uses DNS
    dns().delete(is_error = True)

    interface().delete()

    # no interface
    cifs().delete(is_error=True)

    getInterface(nas)

    cifs().delete()

def t_cifs_standalone():
    nas = getNasServer()
    dns = getDns(nas)
    getInterface(nas)

    cifs = getStandaloneCifsServer(nas)

    deleteNasInstances(nas, [NFS, LDAP, KERBEROS])
    dns().delete()

    cifs().modify()
    cifs().modify()
    cifs().modify(localAdminPassword = "Password123!")

    cifs().delete()
    nas().modify()

    CIFS_SA.create(nas, is_error = True)
    nas().modify()
    cifs = getStandaloneCifsServer(nas)

def t_cifs_rename():
    nas = getNasServer()
    getDns(nas)
    getInterface(nas)

    cifs = getCifsServer(nas)

    cifs().modify()
    cifs().modify()

    cifs().delete()
    cifs = getCifsServer(nas)

    cifs().modify()
    cifs().modify()
    cifs().modify()

def t_cifs_change_type():
    # TODO: think about replication
    pass

def t_cifs_org_unit():
    nas = getNasServer()
    getDns(nas)
    getInterface(nas)
    cifs = getCifsServer(nas)

    [cifs().modify() for _ in range(8)]

def t_cifs_errors():
    nas = getNasServer()
    getDns(nas)
    getInterface(nas)
    deleteNasInstances(nas, [CIFS])

def t_cifs_credentials():
    nas = getNasServer()
    getDns( nas )
    getInterface( nas )
    deleteNasInstances(nas, [CIFS])

    cifs = getCifsServer(nas)
    cifs().modify()

def t_cifs_standalone_errors():
    nas = getNasServer()
    getDns(nas)
    getInterface(nas)
    deleteNasInstances(nas, [CIFS])

    cifs = getCifsServer(nas)

    [cifs().modify() for _ in range(4)]

def t_cifs_skip_unjoin_reuse():
    nas = getNasServer()
    getDns(nas)
    getInterface(nas)
    cifs = getCifsServer(nas)

    cifs().modify()
    cifs().modify()
    cifs().delete()

    Timer.add(30.0)

    cifs = getCifsServer(nas)
    cifs().delete()

    Timer.add(30.0)

    getCifsServer(nas)

def t_cifs_description_field():
    nas = getNasServer()
    getDns(nas)
    getInterface(nas)

    cifs = getCifsServer(nas)
    cifs().modify()

    sa_cifs = getStandaloneCifsServer(nas)
    sa_cifs().modify()
    sa_cifs().delete()

    cifs = getCifsServer(nas)
    [cifs().modify() for _ in range(3)]

if __name__ == '__main__':
    Timer.enable()
    t_cifs_domain()
    t_cifs_standalone()
    t_cifs_rename()
    t_cifs_org_unit()
    t_cifs_errors()
    t_cifs_credentials()
    t_cifs_standalone_errors()
    t_cifs_skip_unjoin_reuse()
    t_cifs_description_field()
    print(Timer.time())