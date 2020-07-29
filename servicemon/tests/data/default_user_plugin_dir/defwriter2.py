from servicemon.plugin_support import AbstractResultWriter


class DefWriter2(AbstractResultWriter, plugin_name='defwriter2',
                 description='Another writer in the default plug-in dir that does nothing.'):

    def begin(self, **kwargs):
        pass

    def one_result(self, stats):
        pass

    def end(self):
        pass
