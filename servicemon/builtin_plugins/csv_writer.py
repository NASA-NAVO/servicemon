import csv
import os
import sys
from pathlib import Path
from datetime import datetime

from servicemon.plugin_support import AbstractResultWriter


class CsvResultWriter(AbstractResultWriter, plugin_name='csv_writer',
                      description='Writes results to a csv file.'):

    def begin(self, args, outfile=None):
        self._first_stat = True
        self._outfile_path = self._compute_outfile_path(args, outfile=outfile)

        # Create the output dir if needed.
        if self._outfile_path is not None:
            os.makedirs(self._outfile_path.parent, exist_ok=True)

    def end(self):
        pass

    def one_result(self, stats):

        if self._outfile_path is not None:
            with open(self._outfile_path, 'a+') as file:
                self._output_stats_row_to_file(stats, file)
        else:
            self._output_stats_row_to_file(stats, sys.stdout)

    def _output_stats_row_to_file(self, stats, file):
        writer = csv.DictWriter(file, dialect='excel',
                                fieldnames=stats.columns())
        if self._first_stat:
            self._first_stat = False
            writer.writeheader()
        writer.writerow(stats.row_values())

    def _compute_outfile_path(self, args, outfile=None):
        """
        If outfile is not None, use it.  Otherwise compute the output file
        name from name of the services file supplied in the args provided.
        """
        result_path = None
        if outfile is not None:
            # Leaving result_path None will cause output to go to stdout.
            if outfile != 'stdout':
                result_path = Path(outfile)
        else:
            now = datetime.now()
            dtstr = now.strftime('%Y-%m-%d-%H:%M:%S.%f')

            base_services_name = Path(args.services).stem
            result_name = f'{base_services_name}_{dtstr}.csv'

            result_path = Path(args.result_dir) / Path(result_name)

        return result_path
