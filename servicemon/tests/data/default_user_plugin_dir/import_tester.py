import requests

from servicemon.plugin_support import AbstractResultWriter


class ImportTester(AbstractResultWriter, plugin_name='import_tester',
                   description='A writer in the default plug-in dir that does nothing but try an import.'):

    def begin(self, args, **kwargs):

        # Test that the import of requests worked.
        print(f'requests = {requests}')

    def one_result(self, stats):
        pass

    def end(self):
        pass
