import time
from datetime import datetime


class QueryStats():
    """
    """
    def __init__(self, name, base_name, service_type, access_url, query_params,
                 result_meta_fields, max_extra_durations=8):

        # First save the params needed to define the result structure.
        self._query_params = self._organize_params(query_params)
        self._result_meta_fields = result_meta_fields
        self._max_extra_durations = max_extra_durations
        self._result_meta = dict.fromkeys(result_meta_fields)

        self._vals = dict.fromkeys(self.columns())

        self._vals['name'] = name
        self._vals['base_name'] = base_name
        self._vals['service_type'] = service_type
        self._vals['access_url'] = access_url
        self._vals['errmsg'] = ':'

        self._query_params = self._organize_params(query_params)
        self._vals.update(self._query_params)  # Add the query_params values.
        self._vals.update(self._result_meta)  # Add the result metadata values.

        self._num_extra_durations = 0

    def add_named_duration(self, name, duration):
        if self._num_extra_durations >= self._max_extra_durations:
            raise ValueError(
                f'Too many intervals added ({self._num_extra_durations + 1})')
        self._vals[f'extra_dur{self._num_extra_durations}_name'] = name
        self._vals[f'extra_dur{self._num_extra_durations}_value'] = duration
        self._num_extra_durations += 1

    def mark_start_time(self):
        now = datetime.fromtimestamp(time.time())
        self._vals['start_time'] = now.strftime('%Y-%m-%d %H:%M:%S.%f')

    def mark_end_time(self):
        now = datetime.fromtimestamp(time.time())
        self._vals['end_time'] = now.strftime('%Y-%m-%d %H:%M:%S.%f')

    @property
    def result_meta(self):
        return self._result_meta

    @property
    def do_query_dur(self):
        return self._vals['do_query_dur']

    @do_query_dur.setter
    def do_query_dur(self, val):
        self._vals['do_query_dur'] = val

    @property
    def stream_to_file_dur(self):
        return self._vals['stream_to_file_dur']

    @stream_to_file_dur.setter
    def stream_to_file_dur(self, val):
        self._vals['stream_to_file_dur'] = val

    @property
    def query_total_dur(self):
        return self._vals['query_total_dur']

    @query_total_dur.setter
    def query_total_dur(self, val):
        self._vals['query_total_dur'] = val

    @property
    def errmsg(self):
        return self._vals['errmsg']

    @errmsg.setter
    def errmsg(self, val):
        self._vals['errmsg'] = val

    @result_meta.setter
    def result_meta(self, value):
        self._result_meta = value
        for key in self._result_meta_fields:
            self._vals[key] = value.get(key)

    def columns(self):
        cols = ['name', 'start_time', 'end_time',
                'do_query_dur', 'stream_to_file_dur', 'query_total_dur']
        for i in range(0, self._max_extra_durations):
            cols.append(f'extra_dur{i}_name')
            cols.append(f'extra_dur{i}_value')
        cols.append('base_name')
        cols.append('service_type')
        cols.append('RA')
        cols.append('DEC')
        cols.append('SR')
        cols.append('ADQL')
        cols.append('other_params')
        cols.append('access_url')
        cols.append('errmsg')
        cols.extend(list(self.result_meta.keys()))
        return cols

    def row_values(self):
        return self._vals

    def _organize_params(self, in_p):
        fixed_keys = ('RA', 'DEC', 'SR', 'ADQL')
        p = dict.fromkeys(fixed_keys, '')
        p['other_params'] = {}
        for key in in_p.keys():
            if key in fixed_keys:
                p[key] = in_p[key]
            else:
                p['other_params'][key] = in_p[key]
        return p
