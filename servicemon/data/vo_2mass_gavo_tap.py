[
    {'base_name': '2MASS_GAVO',
     'service_type': 'tap',
     'access_url': 'http://dc.zah.uni-heidelberg.de/tap',
     'adql': '''
   SELECT
   mainid, raj2000, dej2000, jmag
   FROM twomass.data
   WHERE
      1=CONTAINS(POINT('ICRS', raj2000, dej2000),
                 CIRCLE('ICRS', {}, {}, {} ))
     '''
     },
]
