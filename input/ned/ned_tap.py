[
    {'base_name': 'NED_NED',
     'service_type': 'tap',
     'access_url': 'https://ned.ipac.caltech.edu/tap/',
     'adql':'''
SELECT
   *
   FROM NEDTAP.objdir
   WHERE
      1=CONTAINS(POINT('ICRS', ra, dec),
                 CIRCLE('ICRS', {}, {}, {} ))
     '''
     }
]
