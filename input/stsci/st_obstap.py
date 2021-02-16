[
    {'base_name': 'STScI_ObsTAP',
     'service_type': 'tap',
     'access_url': 'http://vao.stsci.edu/CAOMTAP/TapService.aspx',
     'adql':'''
    SELECT *
    FROM ivoa.obscore
    WHERE
      1=CONTAINS(POINT('ICRS', s_ra, s_dec),
                 CIRCLE('ICRS', {}, {}, {} ))
     '''
     }
]
