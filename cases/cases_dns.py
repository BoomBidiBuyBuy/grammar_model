from model.model_fixtures import load_all
from common import *
from core.timer import Timer

#[globals().update(obj) for obj in load_all()]

def t_dns_list():
    DNS.list()

def t_dns_enable():
    nas = getNasServer(isMultiProtocolEnabled = False)

    deleteNasInstances(nas, [NFS, LDAP, KERBEROS])

    dns = getDns(nas)

    # error case
    DNS.create(nas)

    DNS.modify(dns)
    DNS.modify(dns)

    DNS.delete(dns)

if __name__ == '__main__':
    Timer.enable()
    t_dns_enable()
    print(Timer.time())