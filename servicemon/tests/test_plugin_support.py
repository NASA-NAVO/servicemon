import pytest
from pathlib import Path

from astropy.utils.data import get_pkg_data_filename

from servicemon.plugin_support import SmPluginSupport, AbstractResultWriter, AbstractTimedQuery
from servicemon.query_runner import _parse_query


def load_builtins(capsys):
    SmPluginSupport.load_builtin_plugins()


def load_from_default_user_dir(capsys):
    data_file = get_pkg_data_filename('data/default_user_plugin_dir/basic_writer.py')
    data_dir = Path(data_file).parent
    SmPluginSupport._default_user_plugin_dir = data_dir

    SmPluginSupport.load_plugins()


def load_from_user_dir(capsys):
    plugin_file = get_pkg_data_filename('data/user_plugin_dir/userquery1.py')
    plugin_dir = Path(plugin_file).parent
    SmPluginSupport.load_plugins(plugins=plugin_dir)


def load_from_user_file(capsys):
    plugin_file = get_pkg_data_filename('data/sample_writer.py')
    SmPluginSupport.load_plugins(plugins=plugin_file)


def test_load_plugins(capsys):
    load_builtins(capsys)
    load_from_default_user_dir(capsys)
    load_from_user_dir(capsys)
    load_from_user_file(capsys)

    assert len(AbstractResultWriter._subclasses) == 6  # lengths include the Abstract* base classes.
    assert len(AbstractTimedQuery._subclasses) == 4

    # Check built-ins
    pi = AbstractResultWriter.get_plugin_from_spec('csv_writer:outfile=somedir/somefile.csv')
    assert 'Writes results to a csv file.' in pi.description
    assert pi.cls.__name__ == 'CsvResultWriter'
    assert pi.kwargs['outfile'] == 'somedir/somefile.csv'

    # Check user default dir
    AbstractResultWriter.list_plugins()

    pi = AbstractResultWriter.get_plugin_from_spec('basic_writer')
    assert 'Another writer in the default plug-in dir' in pi.description
    assert pi.cls.__name__ == 'BasicWriter'
    assert pi.kwargs == {}
    _ = pi.cls()   # Instantiates fine since it implements the abstract methods.

    pi = AbstractTimedQuery.get_plugin_from_spec('defquery1:arg1=abc,arg2=def')
    assert 'A query plug-in ' in pi.description
    assert pi.cls.__name__ == 'DefQuery1'
    assert pi.kwargs['arg1'] == 'abc'
    assert pi.kwargs['arg2'] == 'def'

    # Check user plugin dir
    pi = AbstractTimedQuery.get_plugin_from_spec('userquery2')
    assert pi.cls.__name__ == 'UserQuery2'

    pi = AbstractResultWriter.get_plugin_from_spec('cannot_make_reader_instance')
    assert pi.cls.__name__ == 'CannotInstantiate'
    with pytest.raises(TypeError) as record:
        _ = pi.cls()
        assert ("Can't instantiate abstract class CannotInstantiate with abstract methods end"
                in str(record[0].message))

    # Check user file
    pi = AbstractResultWriter.get_plugin_from_spec('sample-writer')
    assert pi.cls.__name__ == 'SampleResultWriter'


def test_imports(capsys):
    load_from_default_user_dir(capsys)
    pi = AbstractResultWriter.get_plugin_from_spec('import_tester')
    pi_instance = pi.cls()

    # Make sure we can run begin() which tries to print out the imported 'requests' module.
    args = _parse_query([
        'fake_services_file.py',
        '--cone_file', 'my_cones.py'
    ])
    pi_instance.begin(args)

    captured = capsys.readouterr()
    output = str(captured.out)
    assert "module 'requests'" in output
