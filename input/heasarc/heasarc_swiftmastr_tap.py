[
    {'base_name': 'HEASARC_swiftmastr',
     'service_type': 'tap',
     'access_url': 'https://heasarc.gsfc.nasa.gov/xamin/vo/tap',
     'adql':'''
SELECT
   *
   FROM swiftmastr
   WHERE 
      1=CONTAINS(POINT('ICRS', ra, dec),
                 CIRCLE('ICRS', {}, {}, {}))
    '''
     }
]
