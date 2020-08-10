import os
import pathlib
import warnings
import traceback
import logging
import html
import requests

from codetiming import Timer

from astropy.coordinates import SkyCoord
from astropy.table import Table
from astroquery.utils import parse_coordinates

from .query_stats import Interval, QueryStats
from .pyvo_wrappers import TAPServiceSM


def time_this(interval_name):
    def time_this_decorator(func):
        def wrapper(*args, **kwargs):
            interval = Interval(interval_name)
            result = func(*args, **kwargs)
            interval.close()
            args[0].stats.add_interval(interval)

            return result
        return wrapper
    return time_this_decorator


class Query():
    """
    """

    def __init__(self, service, coords, radius, out_dir, use_subdir=True,
                 agent='NAVO-servicemon', tap_mode='async', save_results=True,
                 verbose=False):
        self._save_results = save_results

        self._timer = Timer('query_total', logger=None)
        self._timer.timers.clear()

        self.__agent = agent
        self._tap_mode = tap_mode
        self._service = service
        self._base_name = self._compute_base_name()
        self._service_type = self._compute_service_type()
        self._use_subdir = use_subdir

        self._orig_coords = coords
        self._orig_radius = radius
        self._coords = self._compute_coords()
        self._adql = self._compute_adql()
        self._access_url = self._compute_access_url()

        # Add cone params to xcone access_url
        if self._service_type == 'xcone':
            ra, dec, radius = self._get_ra_dec_radius()
            self._access_url = self._access_url.format(ra, dec, radius)

        if self._use_subdir:
            self._out_path = pathlib.Path(f'{out_dir}/{self._base_name}')
        else:
            self._out_path = pathlib.Path(out_dir)
        self._verbose = verbose

        self._query_params = self._compute_query_params()
        self._query_name = self._compute_query_name()
        self._filename = self._out_path / (self._query_name + '.xml')

        self._stats = QueryStats(
            self._query_name, self._base_name, self._service_type,
            self._access_url, self._query_params, self._result_meta_attrs())

    @property
    def stats(self):
        return self._stats

    def run(self):
        with self._timer:
            if self._service_type == 'cone':
                response = self.do_cone_query()
                self.stream_to_file(response)
            if self._service_type == 'xcone':
                response = self.do_xcone_query()
                self.stream_to_file(response)
            elif self._service_type == 'tap':
                tap_service = TAPServiceSM(self._access_url)
                if self._tap_mode == 'async':
                    response = self.do_tap_query_async_pyvo(tap_service)
                else:
                    response = self.do_tap_query_pyvo(tap_service)
                self.stream_to_file(response)

        self.gather_response_metadata(response)

    @time_this('do_query')
    def do_tap_query_async_pyvo(self, tap_service):
        response = tap_service.run_async_timed(self._adql, streamable_response=True)
        return response

    @time_this('do_query')
    def do_tap_query_pyvo(self, tap_service):
        response = tap_service.run_sync_timed(self._adql, streamable_response=True)
        return response

    @time_this('do_query')
    def do_cone_query(self):
        response = self.do_request(self._access_url, self._query_params)
        return response

    @time_this('do_query')
    def do_xcone_query(self):
        response = self.do_request(self._access_url)
        return response

    @time_this('stream_to_file')
    def stream_to_file(self, response):
        os.makedirs(os.path.dirname(self._filename), exist_ok=True)
        with open(self._filename, 'wb+') as fd:
            for chunk in response.iter_content(chunk_size=8096):
                fd.write(chunk)

    def compute_headers(self):
        headers = requests.utils.default_headers()
        if self.__agent is not None:
            headers.update({
                'User-Agent': self.__agent
            })
        return headers

    def do_request(self, url, params=None, agent=None):
        headers = self.compute_headers()

        response = requests.get(url, params, headers=headers, stream=True)
        return response

    def _result_meta_attrs(self):
        return ['status', 'size', 'num_rows', 'num_columns']

    def _handle_exc(self, msg, trace=False):
        self._stats.errmsg = self._stats.errmsg + msg
        if trace:
            traceback.print_exc()
        else:
            logging.error(msg)

    def gather_response_metadata(self, response):
        """
        response:  Either an http.client.HTTPResponse or a yyy
        """
        # Add timings to stats intervals.
        timers = self._timer.timers
        for items in timers.items():
            self._stats.add_interval(Interval(items[0], items[1]))

        result_meta = dict.fromkeys(self._result_meta_attrs())
        result_meta['status'] = response.status_code

        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                t = Table.read(self._filename, format='votable')

            result_meta['size'] = os.path.getsize(self._filename)
            result_meta['num_rows'] = len(t)
            result_meta['num_columns'] = len(t.columns)

            if not self._save_results:
                os.remove(self._filename)
        except Exception as e:
            msg = f'In {self._query_name}, error reading result table: {repr(e)}'
            self._handle_exc(msg)
        finally:
            self._stats.result_meta = result_meta

    def _compute_base_name(self):
        base_name = self.getval(self._service, 'base_name', 'Unnamed')
        return base_name

    def _compute_service_type(self):
        service_type = self.getval(self._service, 'service_type')
        return service_type

    def _compute_access_url(self):
        access_url = self.getval(self._service, 'access_url')
        if access_url is None:
            raise ValueError('service must have an access_url')
        access_url = html.unescape(access_url)

        return access_url

    def _compute_coords(self):
        # Get the RA and Dec from in_coords.
        in_coords = self._orig_coords
        coords = in_coords
        if in_coords is not None:
            if ((type(in_coords) is tuple or type(in_coords) is list) and
                    len(in_coords) == 2):
                coords = SkyCoord(in_coords[0], in_coords[1], frame="icrs",
                                  unit="deg")
            elif type(in_coords) is str:
                coords = parse_coordinates(in_coords)
            elif type(in_coords) is not SkyCoord:
                raise ValueError(f"Cannot parse input coordinates {in_coords}")

        return coords

    def _compute_adql(self):
        adql = self.getval(self._service, 'ADQL', '')
        if adql == '':
            adql = self.getval(self._service, 'adql', '')

        # coords will be None on a replay,
        # since this substitution has already happened.
        if self._coords is not None:
            adql = adql.format(self._coords.ra.deg, self._coords.dec.deg,
                               self._orig_radius)

        return adql

    def _get_ra_dec_radius(self):
        if self._coords is not None:
            ra = self._coords.ra.deg
            dec = self._coords.dec.deg
            radius = self._orig_radius
        else:
            ra = self.getval(self._service, 'RA', None)
            dec = self.getval(self._service, 'DEC', None)
            radius = self.getval(self._service, 'SR', None)

        # Hack because Chandra TAP service does arminutes instead of degrees.
        if self._access_url.startswith('http://cda.harvard.edu/csctap'):
            radius = 60 * radius

        return ra, dec, radius

    def _compute_query_params(self):
        ra, dec, radius = self._get_ra_dec_radius()
        params = {
            'RA': ra,
            'DEC': dec,
            'SR': radius
        }
        if self._service_type == 'tap':
            params['ADQL'] = self.fix_white(self._adql)

        return params

    def _compute_query_name(self):
        name = f'{self._base_name}_{self._service_type}'
        if self._service_type == 'tap':
            name += f'-{self._tap_mode}'
        ra = self._query_params.get('RA')
        dec = self._query_params.get('DEC')
        sr = self._query_params.get('SR')
        if ra is not None and dec is not None and sr is not None:
            name += f'_{ra}_{dec}_{sr}'

        return name

    def getval(self, obj, key, default=None):
        """
        Gets the value as either an attribute val or key val.
        """
        val = getattr(obj, key, None)
        if val is None:
            try:
                val = obj[key]
            except KeyError:
                val = default
        return val

    def fix_white(self, s):
        fixed = " ".join(s.split())
        return fixed
