[
  {'base_name': 'great_archive_tap',
  'service_type': 'tap',
  'access_url': 'http://services.great_archive.net/tap_service',
  'adql':'''
  SELECT *
  FROM ivoa.obscore
  WHERE
    1=CONTAINS(POINT('ICRS', s_ra, s_dec),
              CIRCLE('ICRS', {}, {}, {} ))
  '''
  }
]
