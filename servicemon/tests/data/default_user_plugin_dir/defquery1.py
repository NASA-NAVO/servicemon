from servicemon.plugin_support import AbstractTimedQuery


class DefQuery1(AbstractTimedQuery, plugin_name='defquery1',
                description='A query plug-in that does nothing.'):
    pass
