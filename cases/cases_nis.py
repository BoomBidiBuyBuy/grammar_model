from common import *
from core.timer import Timer

def t_nis_enable():
    nas = getNasServer()

    nis = getNis( nas )

    NIS.create(nas)

    res = NIS.modify(nis, adresses = ['1.1.1.1', '1::34'])

    assert nis().adresses == ['1.1.1.1', '1::34']

    NIS.modify(nis, domain = "spb.2.emc.com")
    assert nis().domain == 'spb.2.emc.com'

    NIS.delete(nis)

def t_nis_auto_switch():
    nas = getNasServer()

    deleteNasInstances(nas, [NFS, NFS_CS, NFS_WS, NIS])

    NAS.modify(nas, currentUnixDirectoryService = "NONE")
    assert nas().currentUnixDirectoryService == "NONE"

    nis = getNis( nas )

    NAS.list()

    NIS.delete(nis)

    NAS.list()

    getInterface( nas )
    getLdap( nas )

    NAS.modify(nas, currentUnixDirectoryService = "LDAP")

    nis = getNis( nas )

    NAS.list()
    assert nas().currentUnixDirectoryService == "LDAP"

    NIS.delete( nis )

    NAS.list()

    NAS.modify(nas, currentUnixDirectoryService = "NONE")

def t_nis_warnings():
    nas = getNasServer()
    deleteNasInstances( nas, [NIS, NFS_CS, NFS_WS] ) # TODO: remove filesystem

    getInterface( nas )

    NAS.modify( nas, currentUnixDirectoryService = "NONE" )

    nis = getNis(nas)
    NIS.modify( nis, domain = 'test-nis.emc.com' )

    NAS.modify( nas, isMultiProtocolEnabled = True, is_error = True)

    getDns( nas )
    getCifsServer( nas )
    getNfs( nas )

    NIS.delete( nis )

    NAS.modify( nas, isMultiProtocolEnabled = True, is_error = True)

    nis = getNis( nas )
    NAS.modify( nas, isMultiProtocolEnabled = True)

    NIS.modify( nis, domain = 'test-nis.emc.com', is_error = True)
    NIS.delete( nis, is_error = True)

    NAS.modify(nas, isMultiProtocolEnabled = False)

if __name__ == '__main__':
    Timer.enable()
    t_nis_enable()
    t_nis_auto_switch()
    t_nis_warnings()
    print(Timer.time())
