import re
from importlib import import_module
from abc import ABC, abstractmethod

from pathlib import Path

from servicemon import builtin_plugins


class SmPluginSupport(ABC):

    _subclasses = {}
    _default_user_plugin_dir = 'plugins'

    @classmethod
    def __init_subclass__(cls, plugin_name=None, description='', **kwargs):
        super().__init_subclass__(**kwargs)
        if plugin_name is None:
            plugin_name = cls.__name__
        cls._subclasses[plugin_name] = SmPluginDesc(plugin_name, cls, description)
        # {'cls': cls, 'description': description}

    @classmethod
    def load_builtin_plugins(cls):
        for dirstr in builtin_plugins.__path__:
            path = Path(dirstr)
            for child in path.iterdir():
                if cls.__is_python_file(child):
                    module = 'servicemon.builtin_plugins.' + child.stem
                    import_module(module)

    @classmethod
    def load_plugins(cls, plugins=None):
        if plugins is None:
            plugins = cls._default_user_plugin_dir

        plugin_path = Path(plugins)
        if cls.__is_python_file(plugin_path):
            cls.__load_file(plugin_path)
        elif plugin_path.is_dir():
            for child in plugin_path.iterdir():
                if cls.__is_python_file(child):
                    cls.__load_file(child)
        else:
            # Only error on non-default file/directory.
            if plugins != cls._default_user_plugin_dir:
                raise FileNotFoundError(f"Plugin file/dir doesn't exist: {plugin_path}")

    @classmethod
    def list_plugins(cls):
        for k in cls._subclasses:
            print(f'subclass key = {k}, value = {cls._subclasses[k]}')

    @classmethod
    def get_plugin(cls, plugin_name):
        plugin = cls._subclasses.get(plugin_name, None)
        return plugin

    @classmethod
    def get_plugin_from_spec(cls, spec):
        parsed = cls.parse_spec(spec)
        plugin = cls.get_plugin(parsed['plugin_name'])
        if plugin is None:
            raise ValueError(f'No plugin found for spec: {spec}')
        full_plugin = SmPluginDesc(plugin.name, plugin.cls, plugin.description, **parsed['kwargs'])
        return full_plugin

    @classmethod
    def parse_spec(cls, spec):
        """
        The plugin specification is a string of the form:

        <plugin> :== <plugin_name> | <plugin_name> ":" <kwargs>
        <kwargs> :== <kwarg> | <kwarg> "," <kwargs>
        <kwarg> :== <key> "=" <value>
        <plugin_name> :== string with no ":"
        <key> :== string with no "=" or ","
        <value> :== string with no ","

        Whitespace will be ignored.

        """
        parsed = None
        stripped = re.sub(r"\s+", "", spec, flags=re.UNICODE)

        # Get the plug-in name.
        matches = re.match(r"^(?P<plugin_name>[^:]*)", stripped)
        if matches is not None:
            next_idx = 0
            parsed = {"plugin_name": matches.group('plugin_name'),
                      "kwargs": {}}

            # Get the keyword arguments.
            while matches is not None:
                next_idx += matches.end() + 1   # Skip the colon or comma, if any.
                matches = re.match(r"(?P<key>[^=,]+)=(?P<value>[^,]+)",
                                   stripped[next_idx:])
                if matches is not None:
                    parsed['kwargs'][matches.group('key')] = matches.group('value')

            # If we didn't finish matching the whole spec, the spec is not valid.
            if next_idx - 1 != len(stripped):
                raise ValueError(f'Invalid plug-in specification: "{spec}"')

        return parsed

    @classmethod
    def __load_file(cls, path: Path):
        python_code = path.read_text(encoding='utf-8')
        compiled_code = compile(python_code, path.name, 'exec')
        exec(compiled_code, globals())

    @classmethod
    def __is_python_file(cls, path: Path):
        is_python_file = path.is_file() and path.suffix == '.py'
        return is_python_file


class SmPluginDesc():
    def __init__(self, name, cls, description, **kwargs):
        self.name = name
        self.cls = cls
        self.description = description
        self.kwargs = kwargs


class AbstractResultWriter(SmPluginSupport):

    _subclasses = {}

    @abstractmethod
    def begin(self, args, **kwargs):
        """
        **args** : argparse.Namespace
            the result of an argparse.ArgumentParser's parse_args().

        **kwargs** : dict
            keyword args from the plug-in specification.
        """
        pass

    @abstractmethod
    def one_result(self, stats):
        """
        **stats** : obj
            an object with the following methods:

            **columns()** : list of str
                list of output column names

            **row_values()** : dict
                dict of output values, one key per column name
        """
        pass

    @abstractmethod
    def end(self):
        pass


class AbstractTimedQuery(SmPluginSupport):

    _subclasses = {}
