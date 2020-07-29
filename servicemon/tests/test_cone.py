import pytest
from servicemon.cone import Cone, _parse_cone_args, conegen_defaults


def errstr(capsys):
    """
    A shortcut with a side effect:  Resets captured stdout and stderr.
    """
    captured = capsys.readouterr()
    result = str(captured.err)
    return result


def validate_cone(num_points, min_radius, max_radius):
    gen = Cone.generate_random(num_points, min_radius, max_radius)
    prev = {'ra': 0, 'dec': 0, 'radius': 0}
    points = list(gen)
    assert len(points) == num_points
    for cone in gen:
        assert 0 <= cone['ra'] < 360
        assert -90 <= cone['dec'] < 90
        assert min_radius <= cone['radius'] <= max_radius

        assert cone['ra'] != prev['ra']
        assert cone['dec'] != prev['dec']
        assert cone['radius'] != prev['radius']

        prev = cone


def test_random():
    validate_cone(100, 0.01, 1.5)
    validate_cone(10000, 14.5, 102)


def test_errors():
    with pytest.raises(ValueError) as e_info:
        Cone.random_cone(2, 1)
    assert ('min-radius must be in the range [0,max_radius).'
            in str(e_info.value))

    with pytest.raises(ValueError) as e_info:
        Cone.generate_random(20, 3, 1)
    assert ('min-radius must be in the range [0,max_radius).'
            in str(e_info.value))

    with pytest.raises(ValueError) as e_info:
        Cone.generate_random(-14, 6, 7)
    assert ('num_points must be a positive number.'
            in str(e_info.value))


def test_parse_args(capsys):

    # With defaults
    args = _parse_cone_args([
        'output_cone_file.py',
        '--num_cones', '27'
    ])
    assert args.outfile == 'output_cone_file.py'
    assert args.num_cones == 27
    assert args.min_radius == conegen_defaults['min_radius']
    assert args.max_radius == conegen_defaults['max_radius']

    # Without defaults
    args = _parse_cone_args([
        'output_cone_file.py',
        '--num_cones', '438',
        '--min_radius', '12.3',
        '--max_radius', '45.6'
    ])
    assert args.outfile == 'output_cone_file.py'
    assert args.num_cones == 438
    assert args.min_radius == 12.3
    assert args.max_radius == 45.6

    # Need outfile
    with pytest.raises(SystemExit):
        _ = _parse_cone_args([
            '--num_cones', '438',
            '--min_radius', '12.3',
            '--max_radius', '45.6'
        ])
    assert ('the following arguments are required: outfile'
            in errstr(capsys))

    # Need num_cones
    with pytest.raises(SystemExit):
        _ = _parse_cone_args([
            'some_file.py',
            '--min_radius', '12.3',
            '--max_radius', '45.6'
        ])
    assert ('the following arguments are required: --num_cones'
            in errstr(capsys))

    # Bad types
    with pytest.raises(SystemExit):
        _ = _parse_cone_args([
            'some_file.py',
            '--num_cones', 'notanint'
        ])
    assert ('--num_cones: invalid int value'
            in errstr(capsys))
    with pytest.raises(SystemExit):
        _ = _parse_cone_args([
            'some_file.py',
            '--min_radius', 'notafloat'
        ])
    assert ('--min_radius: invalid float value'
            in errstr(capsys))
    with pytest.raises(SystemExit):
        _ = _parse_cone_args([
            'some_file.py',
            '--max_radius', 'notafloat'
        ])
    assert ('--max_radius: invalid float value'
            in errstr(capsys))
