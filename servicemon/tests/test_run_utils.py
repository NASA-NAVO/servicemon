import pytest
from servicemon.run_utils import Runner


def parse_args(args):
    runner = Runner()
    parsed_args = runner.parse_args(args)
    return parsed_args


def errstr(capsys):
    """
    A shortcut with a side effect:  Resets captured stdout and stderr.
    """
    captured = capsys.readouterr()
    result = str(captured.err)
    return result


def check_err_msg(capsys, args, msg):
    with pytest.raises(SystemExit):
        args = parse_args(args)
    assert msg in errstr(capsys)


def test_global_args(capsys):
    args = parse_args(['replay', 'testfile.csv', 'outfile.csv'])
    assert not args.batch
    assert not args.norun
    assert not args.verbose

    args = parse_args(['-b', 'replay', 'testfile.csv', 'outfile.csv'])
    assert args.batch
    assert not args.norun
    assert not args.verbose

    args = parse_args(['--batch', 'replay', 'testfile.csv', 'outfile.csv'])
    assert args.batch
    assert not args.norun
    assert not args.verbose

    args = parse_args(['--batch', '--norun', '--verbose',
                       'replay', 'testfile.csv', 'outfile.csv'])
    assert args.batch
    assert args.norun
    assert args.verbose

    args = parse_args(['-b', '-n', '-v',
                       'replay', 'testfile.csv', 'outfile.csv'])
    assert args.batch
    assert args.norun
    assert args.verbose

    check_err_msg(capsys, ['replay', '-b', 'testfile.csv', 'outfile.csv'],
                  'error: unrecognized arguments: -b')

    check_err_msg(capsys, ['replay', '--batch', 'testfile.csv', 'outfile.csv'],
                  'error: unrecognized arguments: --batch')


def test_replay_args(capsys):
    args = parse_args(['replay', 'testfile.csv', 'outfile.csv'])
    assert args.file == 'testfile.csv'

    check_err_msg(capsys, ['replay'],
                  'replay: error: the following arguments are required: file')

    check_err_msg(capsys,
                  ['replay', 'testfile.csv', 'outfile.csv', 'testfile2.csv'],
                  'error: unrecognized arguments: testfile2.csv')

    check_err_msg(capsys, ['replay', '-x', 'testfile.csv', 'outfile.csv'],
                  'error: unrecognized arguments: -x')


def test_query_args(capsys):
    args = parse_args(['query', 'test_service_file', 'test_output_file'])
    assert args.services == 'test_service_file'
    assert args.output == 'test_output_file'

    args = parse_args(['query', 'test_service_file', 'test_outout_file',
                       '--cone-file', 'test_cone_file',
                       '--start-index', '14'])
    assert args.cone_file == 'test_cone_file'
    assert args.start_index == 14

    args = parse_args(['query', 'test_service_file', 'test_outout_file',
                       '--cone-file', 'test_cone_file'])
    assert args.cone_file == 'test_cone_file'
    assert args.start_index == 0

    args = parse_args(['query', 'test_service_file', 'test_outout_file',
                       '--num-cones', '42',
                       '--min-radius', '0.3',
                       '--max-radius', '14.6'])
    assert args.num_cones == 42
    assert args.min_radius == 0.3
    assert args.max_radius == 14.6

    args = parse_args(['query', 'test_service_file', 'test_outout_file',
                       '--num-cones', '42'])
    assert args.num_cones == 42
    assert args.min_radius == 0
    assert args.max_radius == 0.25

    # Error cases

    check_err_msg(capsys, ['query', 'test_service_file', 'test_outout_file',
                           '--num-cones', '42',
                           '--cone-file', 'test_cone_file'],
                  'error: argument --cone-file: '
                  'not allowed with argument --num-cones')

    check_err_msg(capsys, ['query', 'test_service_file', 'test_outout_file',
                           '--min-radius', '23'],
                  'error: argument --num-cones is required when --min-radius '
                  'or --max-radius are present')

    check_err_msg(capsys, ['query', 'test_service_file', 'test_outout_file',
                           '--max-radius', '23'],
                  'error: argument --num-cones is required when --min-radius '
                  'or --max-radius are present')

    check_err_msg(capsys, ['query', 'test_service_file', 'test_outout_file',
                           '--cone-file', 'test_cone_file',
                           '--min-radius', '23'],
                  'error: argument --num-cones is required when --min-radius '
                  'or --max-radius are present')

    check_err_msg(capsys, ['query', 'test_service_file', 'test_outout_file',
                           '--num-cones', '42',
                           '--start-index', '13'],
                  'error: argument --cone-file '
                  'is required when --start-index is present')


def test_conegen_args(capsys):
    args = parse_args(['conegen', 'test_output_file'])
    assert args.output == 'test_output_file'

    args = parse_args(['conegen', 'test_output_file',
                       '--num-cones', '42',
                       '--min-radius', '0.3',
                       '--max-radius', '14.6'])
    assert args.num_cones == 42
    assert args.min_radius == 0.3
    assert args.max_radius == 14.6

    args = parse_args(['conegen', 'test_output_file',
                       '--num-cones', '42'])
    assert args.num_cones == 42
    assert args.min_radius == 0
    assert args.max_radius == 0.25

    # Error cases

    check_err_msg(capsys, ['conegen', 'test_output_file',
                           '--min-radius', '23'],
                  'error: argument --num-cones is required when --min-radius '
                  'or --max-radius are present')

    check_err_msg(capsys, ['conegen', 'test_output_file',
                           '--max-radius', '23'],
                  'error: argument --num-cones is required when --min-radius '
                  'or --max-radius are present')
