from servicemon.plugin_support import AbstractResultWriter


class DefWriter1(AbstractResultWriter, plugin_name='defwriter1',
                 description='A writer in the default plug-in dir that does nothing.'):

    def begin(self, **kwargs):
        pass

    def one_result(self, stats):
        pass

    def end(self):
        pass
