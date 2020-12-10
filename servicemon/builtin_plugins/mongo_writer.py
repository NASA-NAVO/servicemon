import os
import json
import requests

from servicemon.plugin_support import AbstractResultWriter


class MongoDBResultWriter(AbstractResultWriter, plugin_name='mongo_writer',
                          description='Sends results to a remote MongoDB database.'):

    def begin(self, args, outfile=None):

        self._outURL = 'http://vmnavo01.ipac.caltech.edu/cgi-bin/NAVOMonitor/nph-submit'

        self._logFile = '/tmp/servicemon_' + str(os.getpid()) + '.log'

    def end(self):
        pass

    def one_result(self, stats):

        fields = stats.columns()
        self.ncols = len(fields)

        row = stats.row_values()

        jsonStr = json.dumps(row)

        postData = {'json': jsonStr}

        r = requests.post(url=self._outURL, files=postData)

        with open(self._logFile, 'a+') as file:
            file.write(r.text)
