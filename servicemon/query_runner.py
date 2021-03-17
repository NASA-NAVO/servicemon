import sys
import ast
import csv
import signal
import faulthandler
import platform
import logging
import warnings

from argparse import ArgumentParser
from datetime import datetime

from astropy.table import Table
from .query import Query
from .cone import Cone
from .plugin_support import SmPluginSupport, AbstractResultWriter


class QueryRunner():
    """
    """

    _first_instance = True

    def __init__(self, args):
        """
        args is assumed to be a Namespace object args with each attribute having a valid
        value (no defaults will be applied here).  Using vars(args) to show the object as
        a dict would yield an object like this:

        {'cone_file': 'input/cones-10000-0_05-0_25.py',
         'cone_limit': 2,
         'load_plugins': None,
         'max_radius': 0.25,
         'min_radius': 0,
         'norun': True,
         'num_cones': None,
         'result_dir': 'output',
         'save_results': True,
         'services': 'input/stsci/ps_tap.py',
         'start_index': 14,
         'tap_mode': 'async',
         'verbose': False,
         'writers': ['csv_writer:outfile=output/ps-tap-2020-08-02-16:19:37.484191.csv',
         'some_writer']}
        """

        # reset this flag for each instance
        self._first_stat = True

        self._args = args  # All the args rolled up.  We can get rid of the others.

        services = getattr(args, 'services', None)
        if services is not None:
            self._services = self._read_if_file(services)
        else:
            # We must be in replay mode.
            self._services = self._read_if_file(args.file_to_replay)

        # Use getattr for cone_file since it won't exist for replay use cases.
        self._cones = self._read_if_file(getattr(args, 'cone_file', None))

        self._result_dir = args.result_dir
        self._starting_cone = int(args.start_index)
        self._cone_limit = int(args.cone_limit)
        self._tap_mode = args.tap_mode
        self._user_agent = args.user_agent
        self._save_results = args.save_results
        self._verbose = args.verbose
        self._writer_specs = args.writers

        self._writers_descs = []
        self._writers = []
        self._load_plugins(args)

        # This flag will stay False for all future instances.
        self._first_instance = False

    def _load_plugins(self, args):
        if self._first_instance:
            SmPluginSupport.load_builtin_plugins()

            # Load user plugins.
            if args.load_plugins is None:
                SmPluginSupport.load_plugins()
            else:
                SmPluginSupport.load_plugins(plugins=args.load_plugins)

        if self._writer_specs is None:
            # Default to the csv_writer and its default kwargs.
            self._writer_specs = ['csv_writer']

        for spec in self._writer_specs:
            # Substitute time formats in writer templates,
            # such as '%Y-%m-%d %H:%M:%S.%f'
            now = datetime.now()
            spec_with_time = now.strftime(spec)

            plugin = AbstractResultWriter.get_plugin_from_spec(spec_with_time)
            self._writers_descs.append(plugin)

    def run(self):
        """
        """

        self._validate_services(self._services)

        for wdesc in self._writers_descs:
            w = wdesc.cls()
            w.begin(self._args, **wdesc.kwargs)
            self._writers.append(w)

        if self._cones is not None:
            self._run_with_cones()
        else:
            self._run_services_only()

        for w in self._writers:
            w.end()

    def _validate_services(self, services):
        if len(services) == 0:
            warnings.warn('Service list is empty.  Nothing will be timed.')
        else:
            first_stype = self.getval(services[0], 'service_type')
            for service in services[1:]:
                stype = self.getval(service, 'service_type')
                if stype != first_stype:
                    warnings.warn('Differing service_type values found in service list.'
                                  '  Some result writers may fail.')
                    break

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
                                      agent=self._user_agent,
                                      save_results=self._save_results,
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
        cone_index = 0
        cones_run = 0
        for service in self._services:
            if cone_index >= self._starting_cone:
                cones_run += 1
                if cones_run > self._cone_limit:
                    break
                query = Query(service, None, None, self._result_dir,
                              tap_mode=self._tap_mode,
                              agent=self._user_agent,
                              save_results=self._save_results,
                              verbose=self._verbose)
                query.run()
                try:
                    self._collect_stats(query.stats)
                except Exception as e:
                    msg = f'Unable to write stats for service {service}: {repr(e)}'
                    query._handle_exc(msg)

            cone_index += 1

    def _collect_stats(self, stats):
        self._output_stats_row(stats)

    def _output_stats_row(self, stats):
        for w in self._writers:
            w.one_result(stats)

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

    def getval(self, obj, key, default=None):
        """
        Gets the value as either an attribute val or key val.
        """
        val = getattr(obj, key, None)
        if val is None:
            try:
                val = obj[key]
            except KeyError:
                val = default
        return val


################################################################################

# run time routines

conegen_defaults = {
    'min_radius': 0,
    'max_radius': 0.25
}

conelist_defaults = {
    'start_index': 0,
    'cone_limit': 100000000
}


def sm_query(input_args=None):

    args = _parse_query(input_args)

    _init_logging(args)
    _print_arg_info(args)

    # Get the input from the specified file or have it autogenerated.
    if args.cone_file is None:
        args.cone_file = Cone.generate_random(args.num_cones, args.min_radius, args.max_radius)

    # Run the queries
    qr = QueryRunner(args)
    qr.run()


def _parse_query(input_args):
    """
    # Parse args and apply defaults.
    """
    parser = _create_query_argparser()

    # Parse the arguments.  If args is None, then the args implicitly come from sys.argv.
    args = parser.parse_args(input_args)

    # Catch SIGHUP, SIGQUIT and SIGTERM to allow running in the background.
    catch_signals()

    # Validate args.
    if ((args.min_radius is not None or
         args.max_radius is not None) and
            args.num_cones is None):
        parser.error(message='argument --num-cones is required when '
                     '--min-radius or --max-radius are present.')

    if args.num_cones is None and args.cone_file is None:
        parser.error(message='Either --num-cones or --cone_file must be present\n'
                     '   to specify what values go into the service file templates.')

    # Apply defaults that couldn't be built in.
    apply_query_defaults(args, conegen_defaults)
    apply_query_defaults(args, conelist_defaults)
    if args.writers is None:
        # Default to the csv_writer and its default output file.
        args.writers = ['csv_writer']

    return args


def sm_replay(input_args=None):

    args = _parse_replay(input_args)

    _init_logging(args)
    _print_arg_info(args)

    # Run the queries
    qr = QueryRunner(args)
    qr.run()


def _print_arg_info(args):

    # Print arg info and exit if --norun specified
    if args.verbose or args.norun:
        # print arg info
        import pprint
        pp = pprint.PrettyPrinter(width=100, stream=sys.stdout, compact=True)
        arg_values = pp.pformat(vars(args))
        msg = f'Argument values after parsing and applying defaults:\n{arg_values}'

        if args.norun:
            print(msg)
            exit(0)
        else:
            logging.info(msg)


def _parse_replay(input_args):
    """
    # Parse args and apply defaults.
    """
    parser = _create_replay_argparser()

    # Parse the arguments.  If args is None, then the args implicitly come from sys.argv.
    args = parser.parse_args(input_args)

    # Catch SIGHUP, SIGQUIT and SIGTERM to allow running in the background.
    catch_signals()

    # Apply defaults that couldn't be built in.
    apply_query_defaults(args, conelist_defaults)
    if args.writers is None:
        # Default to the csv_writer and its default output file.
        args.writers = ['csv_writer']
    return args


def _create_query_argparser():
    parser = ArgumentParser(description='Measure query performance.')

    # Add positional args.
    parser.add_argument(
        'services', help='File containing list of services to query')

    # Add general args.
    parser.add_argument('-r', '--result_dir', dest='result_dir', default='results',
                        help='The directory in which to put query result files.'
                        ' Unless --save_results is specified, each query result file'
                        ' will be deleted after statistics are gathered for the query.',
                        metavar='result_dir')
    parser.add_argument('-l', '--load_plugins', dest='load_plugins', metavar='plugin_dir_or_file',
                        help='Directory or file from which to load user plug-ins. '
                        'If not specified, and there is a "plugins" subdirectory, plugin '
                        'files will be loaded from there.')
    parser.add_argument('-w', '--writer', dest='writers', action='append',
                        help="Name and kwargs of a writer plug-in to use."
                        "Format is writer_name[:arg1=val1[,arg2=val2...]]"
                        " May appear multiple times to specify multiple writers."
                        " May contain Python datetime format elements which will be"
                        " substituted with appropriate elements of the current time"
                        " (e.g., results-'%%m-%%d-%%H:%%M:%%S'.py)",
                        metavar='writer')
    parser.add_argument('-s', '--save_results', dest='save_results', action='store_true',
                        help='Save the query result data files.  Without this argument, '
                        'the query result file will be deleted after metadata is gathered '
                        'for the query.')
    parser.add_argument('-t', '--tap_mode', dest='tap_mode',
                        choices={'sync', 'async'}, default='async',
                        help='How to run TAP queries (default=async)')
    parser.add_argument('-u', '--user_agent', dest='user_agent',
                        default=None,
                        help='Override the User-Agent used for queries (default=None)')
    parser.add_argument('-n', '--norun', dest='norun', action='store_true',
                        help='Display summary of command arguments without '
                        'performing any actions')
    parser.add_argument('-v', '--verbose', dest='verbose',
                        action='store_true',
                        help='Print additional information to stderr')

    # Add cone arguments.
    cone_types = parser.add_mutually_exclusive_group()
    cone_types.add_argument('--num_cones', type=int, metavar='num_cones',
                            help='Number of cones to generate')
    cone_types.add_argument('--cone_file', metavar='cone_file',
                            help='Path of the file containing the individual query inputs.')

    cone_random = parser.add_argument_group()
    cone_random.add_argument(
        '--min_radius', type=float, help='Minimum radius (deg).'
        f' Default={conegen_defaults["min_radius"]}')
    cone_random.add_argument(
        '--max_radius', type=float, help='Maximum radius (deg).'
        f' Default={conegen_defaults["max_radius"]}')

    cone_file = parser.add_argument_group()
    cone_file.add_argument(
        '--start_index', type=int, metavar='start_index',
        help='Start with this cone in cone file'
        f' Default={conelist_defaults["start_index"]}')
    cone_file.add_argument(
        '--cone_limit', type=int, metavar='cone_limit',
        help='Maximum number of cones to query'
        f' Default={conelist_defaults["cone_limit"]}')

    return parser


def _create_replay_argparser():
    parser = ArgumentParser(description='Measure query replay performance.')

    # Add positional args.
    parser.add_argument('file_to_replay',
                        help='File containing the results of a previous set of query timings.')

    # Add general args.
    parser.add_argument('-r', '--result_dir', dest='result_dir', default='results',
                        help='The directory in which to put query result files.',
                        metavar='result_dir')
    parser.add_argument('-l', '--load_plugins', dest='load_plugins', metavar='plugin_dir_or_file',
                        help='Directory or file from which to load user plug-ins. '
                        'If not specified, and there is a "plugins" subdirectory, plugin '
                        'files will be loaded from there.')
    parser.add_argument('-w', '--writer', dest='writers', action='append',
                        help="Name and kwargs of a writer plug-in to use."
                        "Format is writer_name[:arg1=val1[,arg2=val2...]]"
                        " May appear multiple times to specify multiple writers."
                        " May contain Python datetime format elements which will be"
                        " substituted with appropriate elements of the current time"
                        " (e.g., results-'%%m-%%d-%%H:%%M:%%S'.py)",
                        metavar='writer')
    parser.add_argument('-s', '--save_results', dest='save_results', action='store_true',
                        help='Save the query result data files.  Without this argument, '
                        'the query result file will be deleted after metadata is gathered '
                        'for the query.')
    parser.add_argument('-t', '--tap_mode', dest='tap_mode',
                        choices={'sync', 'async'}, default='async',
                        help='How to run TAP queries (default=async)')
    parser.add_argument('-u', '--user_agent', dest='user_agent',
                        default=None,
                        help='Override the User-Agent used for queries (default=None)')
    parser.add_argument('-n', '--norun', dest='norun', action='store_true',
                        help='Display summary of command arguments without '
                        'performing any actions')
    parser.add_argument('-v', '--verbose', dest='verbose',
                        action='store_true',
                        help='Print additional information to stderr')

    # Add cone arguments.
    parser.add_argument(
        '--start_index', type=int, metavar='start_index',
        help='Start with this cone in cone file'
        f' Default={conelist_defaults["start_index"]}')
    parser.add_argument(
        '--cone_limit', type=int, metavar='cone_limit',
        help='Maximum number of cones to query'
        f' Default={conelist_defaults["cone_limit"]}')

    return parser


def receiveSignal(signalNumber, frame):
    now = datetime.now()
    dtstr = now.strftime('%Y-%m-%d %H:%M:%S.%f')
    logging.warning(f'Received signal {signalNumber} at {dtstr}', file=sys.stderr,
                    flush=True)


def receiveSIGTERM(signalNumber, frame):
    now = datetime.now()
    dtstr = now.strftime('%Y-%m-%d %H:%M:%S.%f')
    logging.warning(f'Received signal {signalNumber} at {dtstr}', file=sys.stderr,
                    flush=True)
    faulthandler.dump_traceback()


def catch_signals():
    """
    Catch SIGHUP, SIGQUIT and SIGTERM to allow running in the background.

    When these signals are caught, a message will go to stderr.

    SIGTERM also cause a stack trace to be sent to stderr.
    """

    # register the signals to be caught
    if platform.system() != 'Windows':
        try:
            signal.signal(signal.SIGHUP, receiveSignal)
        except AttributeError as e:
            logging.warning(f'Warning: unable to add signal.SIGHUP handler: {repr(e)}')

        try:
            signal.signal(signal.SIGQUIT, receiveSignal)
        except AttributeError as e:
            logging.warning(f'Warning: unable to add signal.SIGQUIT handler: {repr(e)}')

    # SIGTERM should be available on Windows.
    try:
        signal.signal(signal.SIGTERM, receiveSignal)
    except AttributeError as e:
        logging.warning(f'Warning: unable to add signal.SIGTERM handler: {repr(e)}')


def apply_query_defaults(parsed_args, defaults):
    for k in defaults:
        if getattr(parsed_args, k) is None:
            setattr(parsed_args, k, defaults[k])


def _enable_requests_logging():
    import http.client as http_client

    http_client.HTTPConnection.debuglevel = 1
    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(logging.DEBUG)
    requests_log.propagate = True


def _init_logging(args):
    level = logging.WARNING

    if (args.verbose):
        level = logging.DEBUG
        _enable_requests_logging()

    logging.basicConfig(format='%(levelname)s: (%(asctime)s)    %(message)s',
                        level=level,
                        datefmt='%Y-%m-%d %H:%M:%S')
