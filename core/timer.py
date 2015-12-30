class Timer(object):
    """
    Singleton that collects time.
    """

    _enabled = False
    _time = 0.0

    #-----------------------#

    def enable():
        Timer._enabled = True

    #-----------------------#

    def disable():
        Timer._enabled = False

    #-----------------------#

    def refresh():
        Timer._time = 0.0

    #-----------------------#

    def add(time):
        if Timer._enabled:
            Timer._time += time

    #-----------------------#

    def time():
        return Timer._time

    #-----------------------#