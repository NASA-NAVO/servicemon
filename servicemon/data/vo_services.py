[
    {'base_name': 'CSC',
     'service_type': 'cone',
     'access_url': 'http://cda.harvard.edu/cscvo/coneSearch?VERB=1&',
     'adql': ''
     },

    # This one uses arcminutes as radius for cone according to docs on
    # http://cxc.harvard.edu/csc2/cli/index.html#vo
    {'base_name': 'CSC',
     'service_type': 'tap',
     'access_url': 'http://cda.harvard.edu/csctap',
     'adql': '''
     SELECT m.name, m.ra, m.dec, m.flux_aper_b FROM master_source m
     WHERE dbo.cone_distance(m.ra,m.dec,{},{})<={}
     '''
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


]
