[
    # This one uses arcminutes as radius for cone according to docs on
    # http://cxc.harvard.edu/csc2/cli/index.html#vo
    {'base_name': 'CSC',
     'service_type': 'tap',
     'access_url': 'http://cda.harvard.edu/csctap',
     'adql': '''
     SELECT m.name, m.ra, m.dec, m.flux_aper_b FROM master_source m
     WHERE dbo.cone_distance(m.ra,m.dec,{},{})<={}
     '''
     }
]
