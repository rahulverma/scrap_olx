from minimock import Mock
from olx.utils import set_now
from datetime import datetime

if __name__ == '__main__':
    from minimock import mock

    from olx.database.persist import get_date
    mock('get_date')

    now = datetime(2013, 11, 6)
    set_now(now)

    import doctest
    from olx.spiders import olx_spider
    doctest.testmod(olx_spider)
