from servicemon.plugin_support import AbstractResultWriter


class BasicWriter(AbstractResultWriter, plugin_name='basic_writer',
                  description='Another writer in the default plug-in dir that does nothing.'):

    def begin(self, args, **kwargs):
        pass

    def one_result(self, stats):
        pass

    def end(self):
        pass
