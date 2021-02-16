[
    {'base_name': 'IPAC_WISE',
     'service_type': 'tap',
     'access_url': 'https://irsa.ipac.caltech.edu/TAP',
     'adql':'''
    SELECT designation, ra, dec FROM allsky_4band_p3as_psd
    WHERE CONTAINS(POINT('ICRS',ra, dec),
    CIRCLE('J2000',{},{},{}))=1
     '''
     }
]
