from servicemon.plugin_support import AbstractTimedQuery


class UserQuery1(AbstractTimedQuery, plugin_name='userquery1',
                 description="A query plug-in in the user's dir that does nothing."):
    pass
