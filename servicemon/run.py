import time
from query_runner import QueryRunner
from cone import Cone

services = [
    {'base_name': 'CSC',
     'service_type': 'cone',
     'access_url': 'http://cda.harvard.edu/cscvo/coneSearch?'
     }
]

cones = [
    {'ra': 125.886, 'dec': 21.3377, 'radius': 0.1},
    {'ra': 125.886, 'dec': 21.3377, 'radius': 0.3}
]


def do_queries():

    stats_path = 'stats/stats_' + str(time.time())
    qr = QueryRunner(services, cones, results_dir='results', stats_path=stats_path)

    qr.run()


def do_random_queries():

    stats_path = 'stats/stats_' + str(time.time())
    random_cones = Cone.generate_random(3, 0.01, 0.04)
    qr = QueryRunner(services, random_cones, results_dir='results', stats_path=stats_path)

    qr.run()


if __name__ == '__main__':
    #    do_queries()
    do_random_queries()
