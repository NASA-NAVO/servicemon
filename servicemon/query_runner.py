from sys import stdout, path
from collections import Iterable
import json
import csv
from query import Query

def from_json_file(source):
    with open(source, 'rb', encoding='utf-8') as data_file:
        data = json.loads(data_file.read())
    return data

def from_table_file(source):
    pass

class QueryRunner():
    """
    """
    
    _first_stat = True
    stats = []
    
    def __init__(self, services, cones, results_dir='.', stats_path=None):
        """
        """
        self._services = services
        self._cones = cones
        self._results_dir = results_dir
        self._stats_path = stats_path
        
    def run(self):
        """
        """
        if self._cones is not None:
            self._run_with_cones()
        else:
            self._run_services_only()
            
    def _run_with_cones(self):
        # print(f'Error handling query: {e}', file=sys.stderr, flush=True)
        for service in self._services:
            for cone in self._cones:
                query = Query(service, (cone['ra'], cone['dec']), cone['radius'], self._results_dir)
                query.run()
                self._collect_stats(query.stats)

    def _run_services_only(self):
        pass
    
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
        writer = csv.DictWriter(stat_file, dialect='excel', fieldnames=stats.columns())
        if self._first_stat:
            self._first_stat = False
            writer.writeheader()
        writer.writerow(stats.row_values())
  
    
    
    
if __name__ == '__main__':
    do_queries()