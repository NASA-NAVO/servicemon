import sys
import signal
import getopt
from datetime import datetime
from query_runner import QueryRunner
from cone import Cone


def compute_stats_path(base_stats_name):
    now = datetime.now()
    dtstr = now.strftime('%Y-%m-%d-%H:%M:%S.%f')
    stats_path = f'stats/{base_stats_name}_{dtstr}.csv'
    return stats_path


def run_ipac_tap():
    stats_path = compute_stats_path('2mass_ipac')
    services = [
        {'base_name': '2MASS_IPAC',
         'service_type': 'tap',
         'access_url': 'https://irsa.ipac.caltech.edu/TAP',
         'adql': '''
        SELECT ra, dec, j_m, h_m, k_m FROM fp_psc
        WHERE CONTAINS(POINT('ICRS',ra, dec),
        CIRCLE('J2000',{},{},{}))=1
         '''
         }
    ]
    qr = QueryRunner(services, 'data/cones.py', results_dir='results',
                     stats_path=stats_path, starting_cone=1)
    qr.run()


def vo_test_fixed_cones():
    stats_path = compute_stats_path('vo_fixed_cones')
    qr = QueryRunner('data/vo_services.py', 'data/cones.py', results_dir='results',
                     stats_path=stats_path)
    qr.run()


def vo_test_random(num_cones):
    stats_path = compute_stats_path('vo_random')
    random_cones = Cone.generate_random(num_cones, 0.01, 0.25)
    qr = QueryRunner('data/vo_services.py', random_cones, results_dir='results',
                     stats_path=stats_path)
    qr.run()


def twomass_random(num_cones):
    stats_path = compute_stats_path('twomass_random')
    random_cones = Cone.generate_random(num_cones, 0.01, 0.25)
    qr = QueryRunner('data/vo_2mass.py', random_cones, results_dir='results',
                     stats_path=stats_path)
    qr.run()


def sample_random(num_cones):
    stats_path = compute_stats_path('sample_random')
    qr = QueryRunner('data/sample.py', [{'ra': 125.886, 'dec': 21.3377, 'radius': 0.05}],
                     results_dir='results', stats_path=stats_path, verbose=True)
    qr.run()


def replay(filename):
    stats_path = compute_stats_path('replay')
    qr = QueryRunner(filename, None, results_dir='results',
                     stats_path=stats_path)
    qr.run()


def run_from_files(base_name, service_file, cone_file, starting_cone):
    stats_path = compute_stats_path(base_name)
    qr = QueryRunner(service_file, cone_file, results_dir='results',
                     stats_path=stats_path, starting_cone=starting_cone)
    qr.run()


def run_with_cone_gen(base_name, service_file, num_cones, min_radius, max_radius):
    stats_path = compute_stats_path(base_name)
    random_cones = Cone.generate_random(num_cones, min_radius, max_radius)
    qr = QueryRunner(service_file, random_cones, results_dir='results',
                     stats_path=stats_path)
    qr.run()


def usage():
    print("""
Usage:
   python run_vo.py <base_name> <service_file> file <cone_file> <starting_cone>
or
   python run_vo.py <base_name> <service_file> <num_cones> <min_radius> <max_radius>
or
   python run_vo.py replay <file>
    """)


def run_cli(argv):
    try:
        opts, args = getopt.getopt(argv, 'h', ['help'])
    except getopt.GetoptError as e:
        print(e)
        usage()
        sys.exit(2)

    for opt, arg in opts:
        if opt in ('-h', '--help'):
            usage()
            sys.exit(0)

    if len(args) != 2 and len(args) != 5:
        usage()
        sys.exit(2)

    if args[0] == 'replay':
        replay(args[1])
    elif args[2] == 'file':
        run_from_files(args[0], args[1], args[3], args[4])
    else:
        run_with_cone_gen(args[0], args[1], args[2],
                          args[3], args[4])


def receiveSignal(signalNumber, frame):
    now = datetime.now()
    dtstr = now.strftime('%Y-%m-%d-%H:%M:%S.%f')
    print(f'Received signal {signalNumber} at {dtstr}', file=sys.stderr, flush=True)


def catch_signals():

    # register the signals to be caught
    signal.signal(signal.SIGHUP, receiveSignal)
    signal.signal(signal.SIGQUIT, receiveSignal)
    signal.signal(signal.SIGTERM, receiveSignal)


def enable_requests_logging():
    import logging
    import http.client as http_client

    http_client.HTTPConnection.debuglevel = 1

    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(logging.DEBUG)
    requests_log.propagate = True


if __name__ == '__main__':

    """
    vo_test_fixed_cones()
    vo_test_random(2)
    twomass_random(1)
    sample_random(1)
    run_ipac_tap()
    replay('stats/twomass_random_2019-03-31-22:56:46.160591.csv')
    run_from_files('PS_Test', 'data/ps_services.py', 'data/cones.py', 0)
    run_from_files('2MASS_Cone_Test', 'data/vo_2mass.py', 'data/cones.py', 0)


    catch_signals()
    run_cli(sys.argv[1:])
    """
    
    catch_signals()
    run_cli(sys.argv[1:])
