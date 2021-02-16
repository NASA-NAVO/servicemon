[
    {'base_name': 'IPAC_2MASS',
     'service_type': 'tap',
     'access_url': 'https://irsa.ipac.caltech.edu/TAP',
     'adql':'''
    SELECT ra, dec, j_m, h_m, k_m FROM fp_psc
    WHERE CONTAINS(POINT('ICRS',ra, dec),
    CIRCLE('J2000',{},{},{}))=1
     '''
     }
]
