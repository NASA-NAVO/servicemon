from servicemon.analysis.stat_queries import StatQueries


def test_build_queries(capsys):
    sq = StatQueries()

    q = sq._build_stat_query()
    assert q == "select * from navostats"

    q = sq._build_stat_query(top=25)
    assert q == "select top 25 * from navostats"

    q = sq._build_stat_query(top=25, base_name='IPAC_%')
    assert q == """select top 25 * from navostats
where
base_name like 'IPAC_%'"""

    q = sq._build_stat_query(top=25, base_name=['IPAC_2MASS', 'GAVO_2MASS'])
    assert q == """select top 25 * from navostats
where
base_name in ('IPAC_2MASS', 'GAVO_2MASS')"""

    q = sq._build_stat_query(top=25, base_name=['IPAC_2MASS', 'GAVO_2MASS'],
                             service_type='tap')
    assert q == """select top 25 * from navostats
where
base_name in ('IPAC_2MASS', 'GAVO_2MASS')
and service_type like 'tap'"""

    q = sq._build_stat_query(top=25, base_name=['IPAC_2MASS', 'GAVO_2MASS'],
                             service_type=['tap', 'cone'])
    assert q == """select top 25 * from navostats
where
base_name in ('IPAC_2MASS', 'GAVO_2MASS')
and service_type in ('tap', 'cone')"""

    q = sq._build_stat_query(top=25, service_type=['tap', 'cone'])
    assert q == """select top 25 * from navostats
where
service_type in ('tap', 'cone')"""

    q = sq._build_stat_query(service_type='cone', start_time='2021-02-01')
    assert q == """select * from navostats
where
service_type like 'cone'
and start_time >= '2021-02-01'"""

    q = sq._build_stat_query(service_type='cone', start_time='2021-02-01',
                             end_time='2021-02-28')
    assert q == """select * from navostats
where
service_type like 'cone'
and start_time >= '2021-02-01'
and end_time <= '2021-02-28'"""
