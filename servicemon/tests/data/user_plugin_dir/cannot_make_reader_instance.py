from servicemon.plugin_support import AbstractResultWriter


class CannotInstantiate(AbstractResultWriter, plugin_name='cannot_make_reader_instance',
                        description="A writer in the user's plug-in dir that cannot be instatiated"
                        " because it doesn't implement the end() method from the abstract base class."):

    def begin(self, args, **kwargs):
        pass

    def one_result(self, stats):
        pass
