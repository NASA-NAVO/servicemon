[
    {'base_name': 'HEASARC_xmmssc',
     'service_type': 'tap',
     'access_url': 'https://heasarc.gsfc.nasa.gov/xamin/vo/tap',
     'adql':'''
SELECT
   *
   FROM xmmssc
   WHERE 
      1=CONTAINS(POINT('ICRS', ra_unc, dec_unc),
                 CIRCLE('ICRS', {}, {}, {} ))
    '''
     }
]
