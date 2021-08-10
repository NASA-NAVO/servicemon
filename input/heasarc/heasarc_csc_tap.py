##  Note that to make the same query at HEASARC and at CXC,
##   their cone_distance() function uses arcmin not degrees
##   like HEASARC's distance() or contains().
[
    {'base_name': 'HEASARC_csc',
     'service_type': 'tap',
     'access_url': 'https://heasarc.gsfc.nasa.gov/xamin/vo/tap',
     'adql':'''
SELECT
   *
   FROM csc
   WHERE 
      1=CONTAINS(POINT('ICRS', ra, dec),
                 CIRCLE('ICRS', {}, {}, {}/60.))
    '''
     }
]
