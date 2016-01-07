from common import *
from core.timer import Timer

def t_ndmp_enable():
    nas = getNasServer()
    deleteNasInstances(nas, [NDMP])

    ndmp = NDMP.create(nas, password = "Password123!")

    # NDMP is already existed on NAS
    NDMP.create(nas, is_error = True)

    NDMP.modify( ndmp, password = "Password456!")

    NDMP.delete( ndmp )

def t_ndmp_errors():
    nas = getNasServer()
    deleteNasInstances(nas, [NDMP])

    # creation without password
    NDMP.create(nas, is_error = True)

    for _ in range(2):
        ndmp = NDMP.create(nas, password = "Password123!")
        NDMP.delete(ndmp)

    for _ in range(5):
        NDMP.create(nas, is_error = True)

    ndmp = getNdmp(nas)

    for _ in range(5):
        NDMP.modify(ndmp, is_error = True)

if __name__ == '__main__':
    Timer.enable()
    t_ndmp_enable()
    t_ndmp_errors()
    print(Timer.time())
