# Add 'AND nDetections > 1' , which eliminates a lot of junk.
[
    {'base_name': 'PanSTARRS',
     'service_type': 'tap',
     'access_url': 'http://vao.stsci.edu/PS1DR2/tapservice.aspx',
     'adql':'''
    SELECT objID, RAMean, DecMean, nDetections, ng, nr, ni, nz, ny, gMeanPSFMag,
    rMeanPSFMag, iMeanPSFMag, zMeanPSFMag, yMeanPSFMag
    FROM dbo.MeanObjectView
    WHERE
    CONTAINS(POINT('ICRS', RAMean, DecMean),CIRCLE('ICRS',{},{},{}))=1
     '''
     },
    {'base_name': 'PanSTARRS',
     'service_type': 'xcone',
     'adql': '',
     'access_url': 'https://catalogs.mast.stsci.edu/api/v0.1/panstarrs/dr2/'
     'mean.votable?flatten_response=false&raw=false&sort_by=distance'
     '&ra={}&dec={}&radius={}'
     }
]
