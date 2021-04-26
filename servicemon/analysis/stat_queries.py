import pyvo as vo


class StatQueries():
    """
    A helper class for querying a TAP service which has `servicemon` data.

    Parameters
    ----------
    tap_url : str, default='http://navo01.ipac.caltech.edu/TAP'
        The endpoint for the TAP service
    table : str, default='navostats2'
        The TAP service table containing the servicemon data

    """

    @property
    def tap_service(self):
        """
        The PyVO TAPService object to be used in queries. Can also be used independently for TAP
        queries outside of `StatQueries` context.

        Returns
        -------
        tap_service : `~pyvo.dal.TAPService`
        """
        return self._tap_service

    def __init__(self, tap_url='http://navo01.ipac.caltech.edu/TAP', table='navostats2'):
        """
        """
        self._tap_service = vo.dal.TAPService(tap_url)
        self._table = table

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
        query = f"select {top_clause}* from {self._table}{where_clause}"

        return query

    def do_query(self, adql):
        """
        Perform the specified synchronous TAP query on the `tap_service`.

        Parameters
        ----------
        adql : str
            The ADQL query to perform
        """
        results = self._tap_service.search(adql)
        data_table = results.to_table()

        return data_table

    def do_stat_query(self, top=None, base_name=None, service_type=None, start_time=None, end_time=None):
        """
        Perform a constrained synchronous TAP query on the `tap_service` and returns an Astropy Table with the results.
        This method will generated the ADQL for the query based on the constraints specified in the parameters.

        Parameters
        ----------
        top : int or str, default=None
            Maximum number of result rows (unlimited if None)
        base_name : str or list of str, default=None
            If a str, it can include ADQL wildcard characters ('%').  If a list of str, wilcards are not supported.
            A row matches if the base_name of the row is an exact match to any of the values in the list.
        service_type : str, default=None
            If a str, it can include ADQL wildcard characters ('%').  If a list of str, wilcards are not supported.
            A row matches if the service_type of the row is an exact match to any of the values in the list.
            Known service_type values include at least 'cone', 'xcone' and 'tap'.  `get_name_service_pairs` will
            show all of the base_name and service_type values currently present in the database.
        start_time : str, default=None
            If specified, rows will be returned only if their start_time value is lexically greater than
            or equal to this `start_time` value.  The start_time format in the database is
            'YYYY-MM-DD HH:MM:SS.dddddd'
            Since this uses a string comparison, the `start_time` need not include the least significant
            portion of the time, e.g., '2021-04-07' would get all data from Apr 7, 2021 onward.
        end_time : str, default=None
            If specified, rows will be returned only if their end_time value is lexically less than or equal to this
            `end_time` value.  The end_time format in the database is
            'YYYY-MM-DD HH:MM:SS.dddddd'
            Since this uses a string comparison, the `end_time` need not include the least significant portion
            of the time, e.g., '2021-04-16' would get all data up to and including Apr 16, 2021.

        Returns
        -------
        data_table : `~astropy.table.table.Table`
        """
        adql = self._build_stat_query(top, base_name, service_type, start_time, end_time)
        data_table = self.do_query(adql)

        return data_table

    def _get_name_service_pairs_query(self):
        query = f"""
        select base_name, service_type from {self._table}
        group by base_name, service_type
        order by base_name"""
        return query

    def get_name_service_pairs(self):
        """
        Queries the database to find all unique (base_name, service_type) pairs and
        returns the results as a list of tuples.  This is effectively a list of all the
        services for which data was collected.

        Returns
        -------
        name_service_pairs : list of (base_name, service_type) tuples


        """

        query = self._get_name_service_pairs_query()
        data_table = self.do_query(query)

        name_service_pairs = [(r['base_name'], r['service_type']) for r in data_table]
        return name_service_pairs
