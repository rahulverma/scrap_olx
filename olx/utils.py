from datetime import datetime

__now = None

def date_today():
    global __now
    if __now:
        return __now
    return datetime.now().date()

def set_now(date):
    global  __now
    __now = date

