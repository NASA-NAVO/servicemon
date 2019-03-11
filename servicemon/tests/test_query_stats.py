import time
from servicemon.query_stats import Interval, QueryStats


def test_interval():
    i = Interval('MyInterval')
    time.sleep(0.001)
    i.close()
    assert i.desc == 'MyInterval'
    assert 0.0 < i.duration < 0.1
    
    
def test_query_stats():
    pass