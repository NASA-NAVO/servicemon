import pytest
from servicemon.query_stats import QueryStats


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
    assert 'meta1' in qs.columns()
    assert 'meta2' in qs.columns()

    qs = QueryStats('Pan-STARRS_random_tap', 'Pan-STARRS_', 'tap',
                    'http://google.com',
                    {'ADQL': 'select cool_stuff from some_table'},
                    {'meta1': 14, 'meta2': 'important data', 'meta3': 42},
                    max_extra_durations=3)
    rv = qs.row_values()
    assert rv['RA'] == ''
    assert rv['DEC'] == ''
    assert rv['SR'] == ''
    assert rv['ADQL'] == 'select cool_stuff from some_table'
    assert rv['other_params'] == {}
    assert 'meta3' in qs.columns()

    qs = QueryStats('HSC_cone_123.4_56.7_8.9', 'HSC', 'cone',
                    'http://google.com',
                    {'RA': 123.4, 'DEC': 56.7, 'SR': 8.9, 'verbose': 3},
                    {'meta1': 14, 'meta2': 'important data'})
    rv = qs.row_values()
    assert rv['other_params']['verbose'] == 3


def test_extra_durations():
    # test 0 allowed
    qs = QueryStats('name', 'base_name', 'service_type',
                    'http://access.url',
                    {'RA': 123.4, 'DEC': 56.7, 'SR': 8.9},
                    {'meta1': 14, 'meta2': 'important data'},
                    max_extra_durations=0)
    with pytest.raises(ValueError) as e_info:
        qs.add_named_duration('toomany', 42)
    assert ('Too many intervals added'
            in str(e_info.value))

    # test 2 allowed
    qs = QueryStats('name', 'base_name', 'service_type',
                    'http://access.url',
                    {'RA': 123.4, 'DEC': 56.7, 'SR': 8.9},
                    {'meta1': 14, 'meta2': 'important data'},
                    max_extra_durations=2)
    qs.add_named_duration('first_dur', 42)
    qs.add_named_duration('second_dur', None)
    with pytest.raises(ValueError) as e_info:
        qs.add_named_duration('toomany', 42)
    assert ('Too many intervals added'
            in str(e_info.value))

    assert 'extra_dur0_name' in qs.columns()
    assert 'extra_dur0_value' in qs.columns()
    assert 'extra_dur1_name' in qs.columns()
    assert 'extra_dur1_value' in qs.columns()
    assert 'extra_dur2_name' not in qs.columns()
    assert 'extra_dur2_value' not in qs.columns()

    rv = qs.row_values()
    assert rv['extra_dur0_name'] == 'first_dur'
    assert rv['extra_dur0_value'] == 42
    assert rv['extra_dur1_name'] == 'second_dur'
    assert rv['extra_dur1_value'] is None

    # test default allowed (8)
    qs = QueryStats('name', 'base_name', 'service_type',
                    'http://access.url',
                    {'RA': 123.4, 'DEC': 56.7, 'SR': 8.9},
                    {'meta1': 14, 'meta2': 'important data'})
    qs.add_named_duration('first_dur', 42)
    qs.add_named_duration('second_dur', 85.2)
    qs.add_named_duration('third_dur', None)
    qs.add_named_duration('fourth_dur', 85.2)
    qs.add_named_duration('fifth_dur', 85.2)
    qs.add_named_duration('sixth_dur', 85.2)
    qs.add_named_duration('seventh_dur', 85.2)
    qs.add_named_duration('eighth_dur', 85.2)
    with pytest.raises(ValueError) as e_info:
        qs.add_named_duration('toomany', 42)
    assert ('Too many intervals added'
            in str(e_info.value))
