from common import *
from core.timer import Timer

def t_dhsm_enable():
    nas = getNasServer()
    deleteNasInstances(nas, [ASA])

    dhsm = ASA.create(nas, password = "Password123!")
    ASA.create(nas, password = "Password123!", is_error = True)

    ASA.modify(dhsm, password = "Password345!")

    ASA.delete(dhsm)

def t_dhsm_error():
    nas = getNasServer()
    deleteNasInstances(nas, [ASA])

    # creation without password
    ASA.create(nas, is_error = True)

    for _ in range(2):
        dhsm = ASA.create(nas, password = "Password123!")
        ASA.delete(dhsm)

    for _ in range(5):
        ASA.create(nas, is_error = True)

    dhsm = getDhsm(nas)

    for _ in range(5):
        ASA.modify(dhsm, is_error = True)

if __name__ == '__main__':
    Timer.enable()
    t_dhsm_enable()
    t_dhsm_error()
    print(Timer.time())