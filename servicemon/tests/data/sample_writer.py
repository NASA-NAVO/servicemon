from servicemon.plugin_support import AbstractResultWriter


class SampleResultWriter(AbstractResultWriter, plugin_name='sample-writer',
                         description='A valid writer that does nothing.'):

    def begin(self, **kwargs):
        pass

    def one_result(self, stats):
        pass

    def end(self):
        pass
