import pyvo as vo


class StatQueries():

    @property
    def tap_service(self):
        return self._tap_service

    def __init__(self, tap_url='http://navo01.ipac.caltech.edu/TAP'):
        """
        """
        self._tap_service = vo.dal.TAPService(tap_url)

    def _build_stat_query(self, top=None, base_name=None, service_type=None, start_time=None, end_time=None):
        """
        """
        where_list = []
        if base_name is not None:
            if isinstance(base_name, str):
                where_list.append(f"base_name like '{base_name}'")
            else:
                bases = ", ".join([f"'{b}'" for b in base_name])
                where_list.append(f"base_name in ({bases})")

        if service_type is not None:
            if isinstance(service_type, str):
                where_list.append(f"service_type like '{service_type}'")
            else:
                types = ", ".join([f"'{s}'" for s in service_type])
                where_list.append(f"service_type in ({types})")

        if start_time is not None:
            where_list.append(f"start_time >= '{start_time}'")
        if end_time is not None:
            where_list.append(f"end_time <= '{end_time}'")

        top_clause = ''if top is None else f'top {top} '
        where_clause = ''
        if where_list:
            where_clause = "\nwhere\n" + "\nand ".join(where_list)
        query = f"select {top_clause}* from navostats{where_clause}"

        return query

    def do_query(self, query):
        results = self._tap_service.search(query)
        data_table = results.to_table()

        return data_table

    def do_stat_query(self, top=None, base_name=None, service_type=None, start_time=None, end_time=None):
        """
        """
        query = self._build_stat_query(top, base_name, service_type, start_time, end_time)
        data_table = self.do_query(query)

        return data_table

    def get_name_service_pairs(self):
        """
        Queries the DB to find all unique (base_name, service_type) pairs and
        returns the results as a list of tuples.
        """

        query = """
        select base_name, service_type from navostats
        group by base_name, service_type
        order by base_name
        """
        data_table = self.do_query(query)

        name_service_pairs = [(r['base_name'], r['service_type']) for r in data_table]
        return name_service_pairs
