#
#  This  needs to be called with uploads={"mytable":"inputs/heasarc/heasarc_nwayawgxmm_votable.xml"}
#  and must be sync not async.  
#
[
    {'base_name': 'HEASARC_cscXupload',
     'service_type': 'tap',
     'access_url': 'https://heasarc.gsfc.nasa.gov/xamin/vo/tap',
     'adql':'''
     SELECT *, DISTANCE(
     POINT('J2000', a.ra, a.dec), 
     POINT('J2000', b.ra, b.dec)
     ) as dist 
     FROM csc as a, tap_upload.mytable as b 
     WHERE 1=CONTAINS(  
     POINT('J2000', a.ra, a.dec),  
     CIRCLE('J2000', b.ra, b.dec, 1)
     ) ORDER BY dist ASC 
     '''
     }
]
