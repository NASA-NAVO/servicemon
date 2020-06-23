from datetime import datetime
import sys
import ast
import csv
import os

from astropy.table import Table
from .query import Query


class QueryRunner():
    """
    """

    _first_stat = True
    stats = []

    def __init__(self, services, cones, result_dir='.', stats_path=None,
                 starting_cone=0, cone_limit=100000000, tap_mode='async',
                 use_pyvo=True, verbose=True):
        """
        """
        self._services = self._read_if_file(services)
        self._cones = self._read_if_file(cones)
        self._result_dir = result_dir
        self._stats_path = stats_path
        self._starting_cone = int(starting_cone)
        self._cone_limit = int(cone_limit)
        self._tap_mode = tap_mode
        self._use_pyvo = use_pyvo
        self._verbose = verbose

        if self._stats_path is not None:
            os.makedirs(os.path.dirname(self._stats_path), exist_ok=True)

    def run(self):
        """
        """
        if self._cones is not None:
            self._run_with_cones()
        else:
            self._run_services_only()

    def _run_with_cones(self):
        cone_index = 0
        cones_run = 0
        for cone in self._cones:
            if cone_index >= self._starting_cone:
                cones_run += 1
                if cones_run > self._cone_limit:
                    break
                for service in self._services:
                    # Don't use the previous results upon new exception.
                    query = None
                    try:
                        query = Query(service, (cone['ra'], cone['dec']),
                                      cone['radius'], self._result_dir,
                                      tap_mode=self._tap_mode,
                                      use_pyvo=self._use_pyvo,
                                      verbose=self._verbose)
                        query.run()
                    except Exception as e:
                        msg = f'Query error for cone {cone}, service {service}: {repr(e)}'
                        query._handle_exc(msg, trace=True)
                    try:
                        self._collect_stats(query.stats)
                    except Exception as e:
                        msg = f'Unable to write stats for cone {cone}, service {service}: {repr(e)}'
                        query._handle_exc(msg)

            cone_index += 1

    def _run_services_only(self):
        for service in self._services:
            try:
                query = Query(service, None, None, self._result_dir,
                              tap_mode=self._tap_mode,
                              use_pyvo=self._use_pyvo,
                              verbose=self._verbose)
                query.run()
            except Exception as e:
                msg = f'Query error for service {service}: {repr(e)}'
                query._handle_exc(msg)
            try:
                self._collect_stats(query.stats)
            except Exception as e:
                msg = f'Unable to write stats for service {service}: {repr(e)}'
                query._handle_exc(msg)

    def _collect_stats(self, stats):
        self.stats.append(stats)
        self._output_stats_row(stats)

    def _output_stats_row(self, stats):
        if self._stats_path is not None:
            with open(self._stats_path, 'a+') as stat_file:
                self._output_stats_row_to_file(stats, stat_file)
        else:
            self._output_stats_row_to_file(stats, sys.stdout)

    def _output_stats_row_to_file(self, stats, stat_file):
        writer = csv.DictWriter(stat_file, dialect='excel',
                                fieldnames=stats.columns())
        if self._first_stat:
            self._first_stat = False
            writer.writeheader()
        writer.writerow(stats.row_values())

    def _read_if_file(self, obj):
        val = obj
        if isinstance(obj, str):
            # Read from file
            if obj.endswith('.py'):
                # read as Python literal, then into Table
                with open(obj, 'r') as f:
                    data = ast.literal_eval(f.read())
                val = Table(rows=data)
            else:
                # assume csv and read into Table
                val = Table.read(obj, format='ascii.csv')
        return val
