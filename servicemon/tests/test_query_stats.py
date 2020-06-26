import time
from servicemon.query_stats import Interval, QueryStats


def test_interval():
    i = Interval('MyInterval')
    time.sleep(0.001)
    i.close()
    assert i.desc == 'MyInterval'
    assert 0.0 < i.duration < 0.1


def test_params():
    qs = QueryStats('HSC_cone_123.4_56.7_8.9', 'HSC', 'cone',
                    'http://google.com',
                    {'RA': 123.4, 'DEC': 56.7, 'SR': 8.9},
                    {'meta1': 14, 'meta2': 'important data'})
    rv = qs.row_values()
    assert rv['RA'] == 123.4
    assert rv['DEC'] == 56.7
    assert rv['SR'] == 8.9
    assert rv['ADQL'] == ''
    assert rv['other_params'] == {}
    assert 'int0_desc' in qs.columns()
    assert 'int0_duration' in qs.columns()
    assert 'int1_desc' in qs.columns()
    assert 'int1_duration' in qs.columns()
    assert 'int8_desc' not in qs.columns()
    assert 'meta1' in qs.columns()
    assert 'meta2' in qs.columns()

    qs = QueryStats('Pan-STARRS_random_tap', 'Pan-STARRS_', 'tap',
                    'http://google.com',
                    {'ADQL': 'select cool_stuff from some_table'},
                    {'meta1': 14, 'meta2': 'important data', 'meta3': 42},
                    max_intervals=3)
    rv = qs.row_values()
    assert rv['RA'] == ''
    assert rv['DEC'] == ''
    assert rv['SR'] == ''
    assert rv['ADQL'] == 'select cool_stuff from some_table'
    assert rv['other_params'] == {}
    assert 'int2_desc' in qs.columns()
    assert 'int2_duration' in qs.columns()
    assert 'meta3' in qs.columns()

    qs = QueryStats('HSC_cone_123.4_56.7_8.9', 'HSC', 'cone',
                    'http://google.com',
                    {'RA': 123.4, 'DEC': 56.7, 'SR': 8.9, 'verbose': 3},
                    {'meta1': 14, 'meta2': 'important data'})
    rv = qs.row_values()
    assert rv['other_params']['verbose'] == 3
