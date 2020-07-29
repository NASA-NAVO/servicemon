from servicemon.plugin_support import AbstractTimedQuery


class UserQuery2(AbstractTimedQuery, plugin_name='userquery2',
                 description="Another query plug-in in the user's dir that does nothing."):
    pass
