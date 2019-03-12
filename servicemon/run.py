import time
from query_runner import QueryRunner
from cone import Cone

services = [
    {'base_name': 'CSC',
     'service_type': 'cone',
     'access_url': 'http://cda.harvard.edu/cscvo/coneSearch?'
     }
]

tap_services = [
    {'base_name': 'STScI_ObsTAP',
     'service_type': 'tap',
     'access_url': 'http://vao.stsci.edu/CAOMTAP/TapService.aspx',
     'adql':'''
SELECT
   *
   FROM ivoa.obscore
   WHERE 
      1=CONTAINS(POINT('ICRS', s_ra, s_dec),
                 CIRCLE('ICRS', {}, {}, {} ))
     '''
     },
    {'base_name': 'PanSTARRS',
     'service_type': 'tap',
     'access_url': 'http://vao.stsci.edu/PS1DR2/tapservice.aspx',
     'adql':'''
    SELECT objID, RAMean, DecMean, nDetections, ng, nr, ni, nz, ny, gMeanPSFMag, rMeanPSFMag, iMeanPSFMag, zMeanPSFMag, yMeanPSFMag
    FROM dbo.MeanObjectView
    WHERE
    CONTAINS(POINT('ICRS', RAMean, DecMean),CIRCLE('ICRS',{},{},{}))=1
    AND nDetections > 1
     '''
     }    
]

cones = [
    {'ra': 125.886, 'dec': 21.3377, 'radius': 0.1},
    {'ra': 125.886, 'dec': 21.3377, 'radius': 0.3}
]

tap_cones = [
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


def do_tap_queries():
    stats_path = 'stats/tapstats_' + str(time.time())
    qr = QueryRunner(tap_services[1:], cones, results_dir='results', stats_path=stats_path)

    qr.run()   
    
def run_bare_tap():
    from astroquery.utils.tap.core import Tap
    
    TAP_service = Tap(url="http://vao.stsci.edu/PS1DR2/tapservice.aspx")
    
    
    job = TAP_service.launch_job_async("""
    SELECT objID, RAMean, DecMean, nDetections, ng, nr, ni, nz, ny, gMeanPSFMag, rMeanPSFMag, iMeanPSFMag, zMeanPSFMag, yMeanPSFMag
    FROM dbo.MeanObjectView
    WHERE
    CONTAINS(POINT('ICRS', RAMean, DecMean),CIRCLE('ICRS',187.706,12.391,.2))=1
    AND nDetections > 1
      """)
    job.wait_for_job_end()
    
    # Adapted from job.__load_async_job_results() and utils.read_http_response()
    subContext = "async/" + str(job.jobid) + "/results/result"
    resultsResponse = job.connHandler.execute_get(subContext) 
    
    results = x
    job.set_results(results)
    
    #TAP_results = job.get_results()   


if __name__ == '__main__':
    #do_queries()
    #    do_random_queries()
    do_tap_queries()
    #run_bare_tap()