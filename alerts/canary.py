# Send regularly scheduled alerts to your email
# like canaries are the first signs of death in the mines,
# this guy will try to warn you about financial death
# (maybe? I'm not that ambitious)
from datetime import datetime


class Canary(object):

    # What do we need?

    # Schedule / Config
    ## Scheduler/cron
    # Alert mechanism (email)
    # Data handling
    ## retrieval
    ## manipulation
    ## formatting

    config = None
    backend = None

    def __init__(self, interval, backend):
        self.config = CanaryConfig(interval)
        self.backend = backend

    def cough(self):


# err, come back to this later,
# interval is enough for now
class CanaryConfig(object):

    interval = 0
    last_run = None

    def __init__(self, interval):
        self.interval = interval