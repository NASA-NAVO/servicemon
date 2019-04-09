import sys
from datetime import datetime
from query_runner import QueryRunner
from cone import Cone


def compute_stats_path(base_stats_name):
    now = datetime.now()
    dtstr = now.strftime('%Y-%m-%d-%H:%M:%S.%f')
    stats_path = f'stats/{base_stats_name}_{dtstr}.csv'
    return stats_path


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
    qr = QueryRunner('data/sample.py', [{'ra': 125.886, 'dec': 21.3377, 'radius': 0.05}],  results_dir='results',
                     stats_path=stats_path, verbose=True)
    qr.run()


def replay(filename):
    stats_path = compute_stats_path('replay')
    qr = QueryRunner(filename, None, results_dir='results',
                     stats_path=stats_path)
    qr.run()
    
def run_from_files(base_name, service_file, cone_file):
    stats_path = compute_stats_path(base_name)
    qr = QueryRunner(service_file, cone_file, results_dir='results',
                     stats_path=stats_path)
    qr.run()
    
def run_with_cone_gen(base_name, service_file, num_cones, min_radius, max_radius):
    stats_path = compute_stats_path(base_name)
    random_cones = Cone.generate_random(num_cones, min_radius, max_radius)
    qr = QueryRunner(service_file, cone_file, results_dir='results',
                     stats_path=stats_path)
    qr.run()
    

if __name__ == '__main__':

    """
    vo_test_fixed_cones()
    vo_test_random(2)
    twomass_random(1)
    sample_random(1)
    replay('stats/twomass_random_2019-03-31-22:56:46.160591.csv')
    """
    if len(sys.argv) != 3 and len(sys.argv) != 5 and len(sys.argv != 6):
        print("""
Usage:
   python run_vo.py base_name service_file "file" cone_file
or
   python run_vo.py base_name service_file num_cones min_radius max_radius
or
   python run_vo.py replay file 
        """)
    else:
        if sys.argv[1] == 'replay':
            replay(sys.argv[2])
        elif sys.argv[3] == 'file':
            run_from_files(sys.argv[1], sys.argv[2], sys.argv[4])
        else:
            run_with_cone_gen(sys.argv[1], sys.argv[2], sys.argv[3],
                              sys.argv[4], sys.argv[5])
    
