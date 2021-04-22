from servicemon.analysis.stat_queries import StatQueries


def test_build_queries(capsys):
    # Test old table name.
    sq = StatQueries(table='navostats')

    q = sq._build_stat_query()
    assert q == "select * from navostats"

    q = sq._get_name_service_pairs_query()
    assert q == """
        select base_name, service_type from navostats
        group by base_name, service_type
        order by base_name"""

    # Use default table name for the rest.
    deftable = 'navostats2'
    sq = StatQueries()

    q = sq._build_stat_query()
    assert q == f"select * from {deftable}"

    q = sq._get_name_service_pairs_query()
    assert q == f"""
        select base_name, service_type from {deftable}
        group by base_name, service_type
        order by base_name"""

    q = sq._build_stat_query(top=25)
    assert q == f"select top 25 * from {deftable}"

    q = sq._build_stat_query(top=25, base_name='IPAC_%')
    assert q == f"""select top 25 * from {deftable}
where
base_name like 'IPAC_%'"""

    q = sq._build_stat_query(top=25, base_name=['IPAC_2MASS', 'GAVO_2MASS'])
    assert q == f"""select top 25 * from {deftable}
where
base_name in ('IPAC_2MASS', 'GAVO_2MASS')"""

    q = sq._build_stat_query(top=25, base_name=['IPAC_2MASS', 'GAVO_2MASS'],
                             service_type='tap')
    assert q == f"""select top 25 * from {deftable}
where
base_name in ('IPAC_2MASS', 'GAVO_2MASS')
and service_type like 'tap'"""

    q = sq._build_stat_query(top=25, base_name=['IPAC_2MASS', 'GAVO_2MASS'],
                             service_type=['tap', 'cone'])
    assert q == f"""select top 25 * from {deftable}
where
base_name in ('IPAC_2MASS', 'GAVO_2MASS')
and service_type in ('tap', 'cone')"""

    q = sq._build_stat_query(top=25, service_type=['tap', 'cone'])
    assert q == f"""select top 25 * from {deftable}
where
service_type in ('tap', 'cone')"""

    q = sq._build_stat_query(service_type='cone', start_time='2021-02-01')
    assert q == f"""select * from {deftable}
where
service_type like 'cone'
and start_time >= '2021-02-01'"""

    q = sq._build_stat_query(service_type='cone', start_time='2021-02-01',
                             end_time='2021-02-28')
    assert q == f"""select * from {deftable}
where
service_type like 'cone'
and start_time >= '2021-02-01'
and end_time <= '2021-02-28'"""
