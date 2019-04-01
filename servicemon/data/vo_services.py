[
    {'base_name': 'CSC',
     'service_type': 'cone',
     'access_url': 'http://cda.harvard.edu/cscvo/coneSearch?',
     'adql': ''
     },

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
     },

    {'base_name': '2MASS_GAVO',
     'service_type': 'cone',
     'access_url': 'http://dc.zah.uni-heidelberg.de/2mass/res/2mass/q/scs.xml?',
     'adql': ''
     },

    {'base_name': '2MASS_STScI',
     'service_type': 'cone',
     'access_url': 'http://dc.zah.uni-heidelberg.de/2mass/res/2mass/q/scs.xml?',
     'adql': ''
     },

    {'base_name': '2MASS_GAVO',
     'service_type': 'cone',
     'access_url': 'http://dc.zah.uni-heidelberg.de/2mass/res/2mass/q/scs.xml?',
     'adql': ''
     },

    {'base_name': '2MASS_GAVO',
     'service_type': 'cone',
     'access_url': 'http://dc.zah.uni-heidelberg.de/2mass/res/2mass/q/scs.xml?',
     'adql': ''
     },
]
