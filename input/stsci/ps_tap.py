[
    {'base_name': 'STScI_PanSTARRS',
     'service_type': 'tap',
     'access_url': 'http://vao.stsci.edu/PS1DR2/tapservice.aspx',
     'adql':'''
   SELECT objID, RAMean, DecMean, nDetections, ng, nr, ni, nz, ny, gMeanPSFMag,
   rMeanPSFMag, iMeanPSFMag, zMeanPSFMag, yMeanPSFMag
   FROM dbo.MeanObjectView
   WHERE
   CONTAINS(POINT('ICRS', RAMean, DecMean),CIRCLE('ICRS',{},{},{}))=1
    '''
     }
]
