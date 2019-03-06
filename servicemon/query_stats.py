import time


class Interval():
    """
    """
    def __init__(self, desc):
        self._desc = desc
        self._start_time = time.time()
        self._end_time = self._start_time

    def close(self):
        self._end_time = time.time()
        return self

    @property
    def desc(self):
        return self._desc

    @property
    def duration(self):
        return self._end_time - self._start_time

    @property
    def start_time(self):
        return self._start_time

    @property
    def end_time(self):
        return self._end_time


class QueryStats():
    """
    """
    def __init__(self, name, base_name, query_type, access_url, query_params,
                 result_meta_fields, max_intervals=2):

        # First save the params needed to define the result structure.
        self._query_params = self._organize_params(query_params)
        self._result_meta_fields = result_meta_fields
        self._max_intervals = max_intervals

        self._vals = dict.fromkeys(self.columns())

        self._vals['name'] = name
        self._vals['base_name'] = base_name
        self._vals['query_type'] = query_type
        self._vals['access_url'] = access_url

        self._query_params = self._organize_params(query_params)
        self._vals.update(self._query_params)  # Add the query_params values.

        self._intervals = []
        self._result_meta = {}

    def add_interval(self, interval):
        lint = len(self._intervals)
        if lint > self._max_intervals:
            raise ValueError(
                f'Too many intervals added ({self._max_intervals + 1})')

        if lint == 0:
            self._vals['start_time'] = time.time()
        self._vals['end_time'] = interval.end_time

        self._vals[f'int{lint}_desc'] = interval.desc
        self._vals[f'int{lint}_duration'] = interval.duration

        self._intervals.append(interval)

    # property result metadata
    @property
    def result_meta(self):
        return self._result_meta

    @result_meta.setter
    def result_meta(self, value):
        self._result_meta = value
        for key in self._result_meta_fields:
            self._vals[key] = value.get(key)

    def columns(self):
        cols = ['name', 'start_time', 'end_time']
        for i in range(0, self._max_intervals):
            cols.append(f'int{i}_desc')
            cols.append(f'int{i}_duration')
        cols.append('base_name')
        cols.append('query_type')
        cols.append('ra')
        cols.append('dec')
        cols.append('sr')
        cols.append('adql')
        cols.append('other_params')
        cols.append('access_url')
        cols.extend(list(self._result_meta.keys()))
        return cols

    def row_values(self):
        return self._vals

    def _organize_params(self, in_p):
        fixed_keys = ('ra', 'dec', 'sr', 'adql')
        p = dict.fromkeys(fixed_keys)
        p['other_params'] = {}
        for key in in_p.keys():
            if key in fixed_keys:
                p[key] = in_p[key]
            else:
                p['other_params'][key] = in_p[key]
        return p
