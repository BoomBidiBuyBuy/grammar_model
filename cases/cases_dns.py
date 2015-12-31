from common import *
from core.timer import Timer

def t_dns_list():
    DNS.list()

def t_dns_enable():
    nas = getNasServer(isMultiProtocolEnabled = False)
    deleteNasInstances(nas, [NFS, LDAP, KERBEROS, CIFS_J, CIFS_SA, NFS_CS, NFS_WS, NFS])

    dns = getDns(nas)

    DNS.create(nas, is_error = True)

    DNS.modify(dns, adresses = ['1.1.1.1', '1::34'])
    assert dns().adresses == ['1.1.1.1', '1::34']
    DNS.modify(dns, domain = 'spb.2.emc.com')
    assert dns().domain == 'spb.2.emc.com'

    DNS.delete(dns)

def t_dns_errors():
    nas = getNasServer()
    deleteNasInstances(nas, [DNS])

    dns = DNS.create(nas)

    for _ in range(2):
        DNS.create(nas, is_error = True)

    for _ in range(25):
        DNS.modify(dns, is_error = True)

    DNS.delete(dns)

def t_dns_async():
    nas = getNasServer(isMultiProtocolEnabled = False)

    deleteNasInstances(nas, [DNS])

    dns = DNS.create(nas)
    DNS.create(nas, is_error = True)

    DNS.modify(dns)
    DNS.modify(dns, is_error = True)

if __name__ == '__main__':
    Timer.enable()
    t_dns_enable()
    t_dns_errors()
    t_dns_async()
    print(Timer.time())