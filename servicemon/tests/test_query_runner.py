import pytest
from servicemon.query_runner import QueryRunner

from servicemon.query_runner import (
    _parse_query, _parse_replay,
    conegen_defaults, conelist_defaults
)


def errstr(capsys):
    """
    A shortcut with a side effect:  Resets captured stdout and stderr.
    """
    captured = capsys.readouterr()
    result = str(captured.err)
    return result


def test_global_query_args(capsys):

    # With defaults.
    args = _parse_query([
        'my_services_file',
        '--cone_file', 'my_cones.py'
    ])
    assert vars(args) == {'cone_file': 'my_cones.py',
                          'cone_limit': conelist_defaults['cone_limit'],
                          'load_plugins': None,
                          'max_radius': conegen_defaults['max_radius'],
                          'min_radius': conegen_defaults['min_radius'],
                          'norun': False,
                          'num_cones': None,
                          'result_dir': 'results',
                          'save_results': False,
                          'services': 'my_services_file',
                          'start_index': conelist_defaults['start_index'],
                          'tap_mode': 'async',
                          'verbose': False,
                          'writers': ['csv_writer']}

    # Without defaults for auto-generated cones.
    args = _parse_query([
        'my_services_file',
        '--load_plugins', 'my_plugin_dir',
        '--writer', 'my_writer1', '--writer', 'my_writer2:karg1=val1,kwarg2=val2',
        '--result_dir', 'my_output_dir',
        '--save_results', '--tap_mode', 'sync', '--norun', '--verbose',
        '--num_cones', '22', '--min_radius', '0.123', '--max_radius', '0.456',
        '--start_index', '17', '--cone_limit', '3'
    ])
    assert vars(args) == {'cone_file': None,
                          'cone_limit': 3,
                          'load_plugins': 'my_plugin_dir',
                          'max_radius': 0.456,
                          'min_radius': 0.123,
                          'norun': True,
                          'num_cones': 22,
                          'result_dir': 'my_output_dir',
                          'save_results': True,
                          'services': 'my_services_file',
                          'start_index': 17,
                          'tap_mode': 'sync',
                          'verbose': True,
                          'writers': ['my_writer1', 'my_writer2:karg1=val1,kwarg2=val2']}

    # Without defatults for cone_file specified.
    args = _parse_query([
        'my_services_file',
        '--result_dir', 'my_output_dir',
        '--load_plugins', 'my_plugin_dir',
        '--writer', 'my_writer1', '--writer', 'my_writer2:karg1=val1,kwarg2=val2',
        '--save_results', '--tap_mode', 'sync', '--norun', '--verbose',
        '--cone_file', 'fun_cone_file.py',
        '--start_index', '13', '--cone_limit', '44'
    ])
    assert vars(args) == {'cone_file': 'fun_cone_file.py',
                          'cone_limit': 44,
                          'load_plugins': 'my_plugin_dir',
                          'max_radius': conegen_defaults['max_radius'],
                          'min_radius': conegen_defaults['min_radius'],
                          'norun': True,
                          'num_cones': None,
                          'result_dir': 'my_output_dir',
                          'save_results': True,
                          'services': 'my_services_file',
                          'start_index': 13,
                          'tap_mode': 'sync',
                          'verbose': True,
                          'writers': ['my_writer1', 'my_writer2:karg1=val1,kwarg2=val2']}

    # With short args
    args = _parse_query([
        'my_services_file',
        '-l', 'my_plugin_dir',
        '-w', 'my_writer1', '--writer', 'my_writer2:karg1=val1,kwarg2=val2',
        '-s', '-t', 'sync', '-n', '-v',
        '--cone_file', 'fun_cone_file.py',
        '--start_index', '13', '--cone_limit', '44'
    ])
    assert vars(args) == {'cone_file': 'fun_cone_file.py',
                          'cone_limit': 44,
                          'load_plugins': 'my_plugin_dir',
                          'max_radius': conegen_defaults['max_radius'],
                          'min_radius': conegen_defaults['min_radius'],
                          'norun': True,
                          'num_cones': None,
                          'result_dir': 'results',
                          'save_results': True,
                          'services': 'my_services_file',
                          'start_index': 13,
                          'tap_mode': 'sync',
                          'verbose': True,
                          'writers': ['my_writer1', 'my_writer2:karg1=val1,kwarg2=val2']}


def test_global_query_arg_errors(capsys):
    with pytest.raises(SystemExit):
        _ = _parse_query([])
    assert ('error: the following arguments are required: service'
            in errstr(capsys))

    with pytest.raises(SystemExit):
        _ = _parse_query(['service_file_only.py'])
    assert ('Either --num-cones or --cone_file must be present'
            in errstr(capsys))

    with pytest.raises(SystemExit):
        _ = _parse_query(['service_file.py',
                          '--min_radius', '0.123',
                          '--max_radius', '0.456'])
    assert ('argument --num-cones is required when --min-radius or --max-radius are present.'
            in errstr(capsys))

    with pytest.raises(SystemExit):
        _ = _parse_query(['service_file.py',
                          '--max_radius', '0.456'])
    assert ('argument --num-cones is required when --min-radius or --max-radius are present.'
            in errstr(capsys))

    # No short arg for cone_file.
    with pytest.raises(SystemExit):
        _ = _parse_query(['service_file.py',
                          '-c', 'some_cone_file.py'])
    assert ('unrecognized arguments: -c'
            in errstr(capsys))


def test_global_replay_args(capsys):

    # With defaults.
    args = _parse_replay([
        'file_to_replay.csv'
    ])
    assert vars(args) == {'cone_limit': 100000000,
                          'file_to_replay': 'file_to_replay.csv',
                          'load_plugins': None,
                          'norun': False,
                          'result_dir': 'results',
                          'save_results': False,
                          'start_index': 0,
                          'tap_mode': 'async',
                          'verbose': False,
                          'writers': ['csv_writer']}

    # Without defaults.
    args = _parse_replay([
        'file_to_replay.csv',
        '--load_plugins', 'my_plugin_dir',
        '--writer', 'my_writer1', '--writer', 'my_writer2:karg1=val1,kwarg2=val2',
        '--result_dir', 'my_output_dir',
        '--save_results', '--tap_mode', 'sync', '--norun', '--verbose',
        '--start_index', '17', '--cone_limit', '3'
    ])
    assert vars(args) == {'cone_limit': 3,
                          'file_to_replay': 'file_to_replay.csv',
                          'load_plugins': 'my_plugin_dir',
                          'norun': True,
                          'result_dir': 'my_output_dir',
                          'save_results': True,
                          'start_index': 17,
                          'tap_mode': 'sync',
                          'verbose': True,
                          'writers': ['my_writer1', 'my_writer2:karg1=val1,kwarg2=val2']}


def test_global_replay_arg_errors(capsys):

    # cone_file is not available for replay.
    with pytest.raises(SystemExit):
        _ = _parse_replay(['file_to_replay.csv',
                          '--cone_file', 'some_cone_file.py'])
    assert ('unrecognized arguments: --cone_file'
            in errstr(capsys))


def test_service_validation(capsys):
    args = _parse_query([
        'fake_services_file',
        '--cone_file', 'my_cones.py'
    ])
    args.services = []
    args.cone_file = []
    qr = QueryRunner(args)
    with pytest.warns(UserWarning, match='Service list is empty') as record:
        qr._validate_services(args.services)
    assert len(record) == 1

    args.services = [
        {'service_type': 'tap'},
        {'service_type': 'tap'},
        {'service_type': 'tap'},
    ]
    with pytest.warns(None) as record:
        qr._validate_services(args.services)
    assert len(record) == 0

    args.services = [
        {'service_type': 'tap'},
        {'service_type': 'cone'},
        {'service_type': 'tap'},
    ]
    with pytest.warns(UserWarning,
                      match='Differing service_type values found in service list.'
                      '  Some result writers may fail.') as record:
        qr._validate_services(args.services)
    assert len(record) == 1
