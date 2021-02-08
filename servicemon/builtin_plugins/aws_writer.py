import os
import json
import socket
import requests
import datetime

from ec2_metadata import ec2_metadata

from servicemon.plugin_support import AbstractResultWriter


class AWSResultWriter(AbstractResultWriter, plugin_name='aws_writer',
                      description='Sends results to a central SQLite database.'):

    # BEGIN gathers info and sends a 'begin' state message
    # to the admin database

    def begin(self, args, outfile=None):

        self._pid = os.getpid()

        self._starttime = str(datetime.datetime.now())

        self._adminURL = 'http://vmnavo01.ipac.caltech.edu/cgi-bin/NAVOMonitor/nph-admin'
        self._resultsURL = 'http://vmnavo01.ipac.caltech.edu/cgi-bin/NAVOMonitor/nph-submit'

        try:
            self._region = ec2_metadata.region
            self._instance_id = ec2_metadata.instance_id
            self._hostname = ec2_metadata.public_hostname

        except Exception:
            self._region = ''
            self._instance_id = ''
            self._hostname = socket.getfqdn()

        if len(self._region) > 0:
            self._location = self._region
        else:
            self._location = self._hostname

        data = {'hostname': self._hostname, 'pid': self._pid,
                'region': self._region, 'instance_id': self._instance_id,
                'starttime': self._starttime, 'endtime': ''}

        jsonStr = json.dumps(data)

        print("START> ", jsonStr)

        post_data = {'json': jsonStr}

        r = requests.post(url=self._adminURL, files=post_data)

        print(r.text)

    # END sends an 'end' state message to the admin database,
    # potentially triggering shutdown/clean-up

    def end(self):

        endtime = str(datetime.datetime.now())

        data = {'hostname': self._hostname, 'pid': self._pid,
                'region': self._region, 'instance_id': self._instance_id,
                'starttime': self._starttime, 'endtime': endtime}

        jsonStr = json.dumps(data)

        print("END>   ", jsonStr)

        post_data = {'json': jsonStr}

        r = requests.post(url=self._adminURL, files=post_data)

        print(r.text)

    # ONE_RESULT sends a data record (the results on a single query)
    # to the results database

    def one_result(self, stats):

        fields = stats.columns()

        self.ncols = len(fields)

        row = stats.row_values()

        row['location'] = self._location

        print('DATA> ' + str(row))

        jsonStr = json.dumps(row)

        post_data = {'json': jsonStr}

        r = requests.post(url=self._resultsURL, files=post_data)

        print(r.text)
