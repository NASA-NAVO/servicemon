import os
import shutil
import pytest
from pathlib import Path
from datetime import datetime

from astropy.table import Table
from servicemon.plugin_support import SmPluginSupport, AbstractResultWriter
from servicemon.query_runner import _parse_query


def errstr(capsys):
    """
    A shortcut with a side effect:  Resets captured stdout and stderr.
    """
    captured = capsys.readouterr()
    result_err = str(captured.err)
    result_out = str(captured.out)
    return result_err, result_out


@pytest.fixture
def cleandirs():
    # Clean before
    shutil.rmtree(Path('my_fake_result_dir'), ignore_errors=True)
    shutil.rmtree(Path('my_fake_result_dir2'), ignore_errors=True)
    yield
    # And after
    shutil.rmtree(Path('my_fake_result_dir'), ignore_errors=True)
    shutil.rmtree(Path('my_fake_result_dir2'), ignore_errors=True)


def test_end(capsys):
    SmPluginSupport.load_builtin_plugins()

    # Test with no input args.
    cw = begin_no_outfile()
    cw.end()


@pytest.mark.usefixtures("cleandirs")
def test_begin(capsys):
    SmPluginSupport.load_builtin_plugins()
    now = datetime.now()
    dtstr = now.strftime('%Y-%m-%d')

    # Test with no input args.
    cw = begin_no_outfile()
    assert isinstance(cw._outfile_path, Path)
    assert cw._outfile_path.stem.startswith(f'fake_services_file_{dtstr}')
    assert cw._outfile_path.parent.name == 'my_fake_result_dir'
    os.rmdir('my_fake_result_dir')

    # Test with outfile specified with fixed dstr.  Dstring substitutions are not done at this level.
    cw = begin_w_outfile(dtstr)
    assert isinstance(cw._outfile_path, Path)
    assert cw._outfile_path.name == f'myout-{dtstr}.csv'
    assert cw._outfile_path.parent.name == 'my_fake_result_dir2'
    os.rmdir('my_fake_result_dir2')

    # Test with outfile as stdout
    cw = begin_outfile_stdout()
    assert cw._outfile_path is None
    assert not Path('my_fake_result_dir3').exists()


@pytest.mark.usefixtures("cleandirs")
def test_one_result(capsys):
    SmPluginSupport.load_builtin_plugins()

    # Test with specified outfile.
    cw = begin_w_outfile('nodate')
    resfile = write_some_results(cw)

    # Read and check results.
    t = Table.read(resfile, format='csv')
    assert_table_vals(t)

    # Test with stdout.
    cw = begin_outfile_stdout()
    resfile = write_some_results(cw)
    _, out = errstr(capsys)
    t = Table.read(out, format='csv')
    assert_table_vals(t)


def assert_table_vals(t):
    assert len(t) == 2
    assert t['a'][0] == '1'
    assert t['a'][1] == 'vala'
    assert t['b'][0] == '2'
    assert t['b'][1] == 'valb'
    assert t['c'][0] == '3'
    assert t['c'][1] == 'valc'


def write_some_results(cw):
    resfile = Path('my_fake_result_dir2') / Path('myout-nodate.csv')
    results = Results(['a', 'b', 'c'])
    results.set_values({'a': 1, 'b': 2, 'c': 3})
    cw.one_result(results)
    results.set_values({'a': 'vala', 'b': 'valb', 'c': 'valc'})
    cw.one_result(results)
    return resfile


def begin_outfile_stdout():
    args = _parse_query([
        'fake_services_file.py',
        '--cone_file', 'my_cones.py',
        '--result_dir', 'my_fake_result_dir3'
    ])
    cw_plugin = AbstractResultWriter.get_plugin_from_spec('csv_writer:outfile=stdout')
    cw = cw_plugin.cls()
    cw.begin(args, **cw_plugin.kwargs)
    return cw


def begin_w_outfile(dtstr):
    args = _parse_query([
        'fake_services_file.py',
        '--cone_file', 'my_cones.py',
        '--result_dir', 'my_fake_result_dir2'
    ])
    cw_plugin = AbstractResultWriter.get_plugin_from_spec(f'csv_writer:outfile=my_fake_result_dir2/myout-{dtstr}.csv')
    cw = cw_plugin.cls()
    cw.begin(args, **cw_plugin.kwargs)
    return cw


def begin_no_outfile():
    args = _parse_query([
        'fake_services_file.py',
        '--cone_file', 'my_cones.py',
        '--result_dir', 'my_fake_result_dir'
    ])
    cw_plugin = AbstractResultWriter.get_plugin_from_spec('csv_writer')
    cw = cw_plugin.cls()
    cw.begin(args, **cw_plugin.kwargs)
    return cw


class Results():
    def __init__(self, cols):
        self._cols = cols
        self._vals = [None] * len(self._cols)

    def set_values(self, vals):
        if len(vals) != len(self._cols):
            raise ValueError('values must have same length as columns.')
        self._vals = vals

    def columns(self):
        return self._cols

    def row_values(self):
        return self._vals
