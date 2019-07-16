import sys
import signal
import warnings
warnings.filterwarnings("ignore", message='astropy.extern.six will be removed')

from argparse import ArgumentParser
from datetime import datetime
from .query_runner import QueryRunner
from .cone import Cone


class Runner():

    conegen_defaults = {
        'min_radius': 0,
        'max_radius': 0.25
    }

    conelist_defaults = {
        'start_index': 0
    }

    def _apply_query_defaults(self, parsed_args, defaults):
        for k in defaults:
            if getattr(parsed_args, k) is None:
                setattr(parsed_args, k, defaults[k])

    def _create_parser(self):
        parser = ArgumentParser(description='Measure service performance.')

        parser.add_argument('-b', '--batch', dest='batch', action='store_true',
                            help='Catch SIGHUP, SIGQUIT and SIGTERM'
                            ' to allow running in the background')
        parser.add_argument('-n', '--norun', dest='norun', action='store_true',
                            help='Display summary of command arguments without'
                            'performing any actions')
        parser.add_argument('-v', '--verbose', dest='verbose',
                            action='store_true',
                            help='Print additional information to stdout')

        sps = parser.add_subparsers(dest='command',
                                    metavar='conegen|replay|query')
        sps.required = True

        conegen = sps.add_parser('conegen',
                                 description='Generate random cones',
                                 help='Generate random cones')
        conegen.add_argument(
            'output', help="Name of the output file to contain the cones. "
            " May contain Python datetime format elements which will be"
            " substituted with appropriate elements of the current time"
            " (e.g., conefile-'%%m-%%d-%%H:%%M:%%S'.py)")
        conegen_args = conegen.add_argument_group()
        conegen_args.add_argument(
            '--num-cones', type=int, help='Number of cones to generate')
        conegen_args.add_argument(
            '--min-radius', type=float, help='Minimum radius (deg).'
            f' Default={self.conegen_defaults["min_radius"]}')
        conegen_args.add_argument(
            '--max-radius', type=float, help='Maximum radius (deg).'
            f' Default={self.conegen_defaults["max_radius"]}')

        replay = sps.add_parser(
            'replay',
            description='Replay queries from a previous result file.',
            help='Replay queries from a previous result file.')
        replay.add_argument('file', help='The file to replay.')
        replay.add_argument(
            'output', help="Name of the output file to contain the cones. "
            " May contain Python datetime format elements which will be"
            " substituted with appropriate elements of the current time"
            " (e.g., replay-timing-'%%m-%%d-%%H:%%M:%%S'.csv)")

        query = sps.add_parser(
            'query', description='Query a list of services',
            help='Query a list of services')
        query.add_argument(
            'services', help='File containing list of services to query')
        query.add_argument(
            'output', help="Name of the output file to contain the cones. "
            " May contain Python datetime format elements which will be"
            " substituted with appropriate elements of the current time"
            " (e.g., query-timing-'%%m-%%d-%%H:%%M:%%S'.csv)")

        cone_types = query.add_mutually_exclusive_group()
        cone_types.add_argument(
            '--num-cones', type=int, help='Number of cones to generate')
        cone_types.add_argument('--cone-file')

        cone_random = query.add_argument_group()
        cone_random.add_argument(
            '--min-radius', type=float, help='Minimum radius (deg).'
            f' Default={self.conegen_defaults["min_radius"]}')
        cone_random.add_argument(
            '--max-radius', type=float, help='Maximum radius (deg).'
            f' Default={self.conegen_defaults["max_radius"]}')

        cone_file = query.add_argument_group()
        cone_file.add_argument('--start-index', type=int)

        return parser

    def _validate_args(self, parser, args):
        if args.command == 'query' or args.command == 'conegen':
            if ((args.min_radius is not None or
                 args.max_radius is not None) and
                    args.num_cones is None):
                parser.error(message='argument --num-cones is required when '
                             '--min-radius or --max-radius are present.')

        if args.command == 'query':
            if args.start_index is not None and args.cone_file is None:
                parser.error(message='argument --cone-file is required when '
                             '--start-index is present.')

    def parse_args(self, args):
        parser = self._create_parser()
        parsed_args = parser.parse_args(args)

        # Custom validation and defaults
        self._validate_args(parser, parsed_args)
        if parsed_args.command == 'query':
            self._apply_query_defaults(parsed_args, self.conegen_defaults)
            self._apply_query_defaults(parsed_args, self.conelist_defaults)
        if parsed_args.command == 'conegen':
            self._apply_query_defaults(parsed_args, self.conegen_defaults)

        # Substitute time formats in output file name template,
        # such as '%Y-%m-%d-%H:%M:%S.%f'
        now = datetime.now()
        time_outfile = now.strftime(parsed_args.output)
        parsed_args.output = time_outfile

        if parsed_args.verbose or parsed_args.norun:
            self.print_arg_info(parsed_args)

        return parsed_args

    def print_arg_info(self, args):
        print(f'''
Options:
batch: {args.batch}
norun: {args.norun}
verbose: {args.verbose}''')

        if args.command == 'replay':
            print(f'''
Replaying: {args.file}
Output: {args.output}''')
        elif args.command == 'query':
            print(f'''
Services: {args.services}
Output: {args.output}''')
            if args.cone_file is not None:
                print(f'''
Cones: {args.cone_file} [{args.start_index}:]''')
            elif args.num_cones is not None:
                print(f'''
{args.num_cones} random cones,
min-radius: {args.min_radius}, max-radius: {args.max_radius}''')

    def run_cl(self, args):
        pa = self.parse_args(args=args)

        if pa.batch:
            self.catch_signals()

        if not pa.norun:
            if pa.command == 'replay':
                self.replay(pa.file, pa.output, pa.verbose)

            elif pa.command == 'query':
                if pa.cone_file is not None:
                    self.query_from_cone_file(pa.services, pa.output,
                                              pa.cone_file, pa.start_index,
                                              pa.verbose)

                elif pa.num_cones is not None:
                    self.query_with_cone_gen(pa.services, pa.output,
                                             pa.num_cones, pa.min_radius,
                                             pa.max_radius, pa.verbose)
            elif pa.command == 'conegen':
                Cone.write_random(pa.num_cones, pa.min_radius, pa.max_radius,
                                  filename=pa.output)

    def replay(self, filename, output, verbose):
        qr = QueryRunner(filename, None, results_dir='results',
                         stats_path=output, verbose=verbose)
        qr.run()

    def query_from_cone_file(self, service_file, output, cone_file,
                             starting_cone, verbose):
        qr = QueryRunner(service_file, cone_file, results_dir='results',
                         stats_path=output, starting_cone=starting_cone,
                         verbose=verbose)
        qr.run()

    def query_with_cone_gen(self, service_file, output, num_cones, min_radius,
                            max_radius, verbose):
        random_cones = Cone.generate_random(num_cones, min_radius, max_radius)
        qr = QueryRunner(service_file, random_cones, results_dir='results',
                         stats_path=output, verbose=verbose)
        qr.run()

    def receiveSignal(self, signalNumber, frame):
        now = datetime.now()
        dtstr = now.strftime('%Y-%m-%d-%H:%M:%S.%f')
        print(f'Received signal {signalNumber} at {dtstr}', file=sys.stderr,
              flush=True)

    def catch_signals(self):

        # register the signals to be caught
        signal.signal(signal.SIGHUP, self.receiveSignal)
        signal.signal(signal.SIGQUIT, self.receiveSignal)
        signal.signal(signal.SIGTERM, self.receiveSignal)

    def enable_requests_logging(self):
        import logging
        import http.client as http_client

        http_client.HTTPConnection.debuglevel = 1

        logging.basicConfig()
        logging.getLogger().setLevel(logging.DEBUG)
        requests_log = logging.getLogger("requests.packages.urllib3")
        requests_log.setLevel(logging.DEBUG)
        requests_log.propagate = True
