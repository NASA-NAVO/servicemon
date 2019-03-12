from astropy.coordinates import SkyCoord
from astropy.table import Table
from astroquery.utils import parse_coordinates

import warnings

import html
import requests
import os
import sys
import pathlib

from query_stats import Interval, QueryStats

def get_data():
    "Just for testing testing"
    return ['012345678901234567890123456']

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

    def __init__(self, service, coords, radius, out_dir, verbose=False):
        self._service = service
        self._base_name = self._compute_base_name()
        self._service_type = self._compute_service_type()
        self._access_url = self._compute_access_url()
        
        self._orig_coords = coords
        self._orig_radius = radius
        self._coords = self._compute_coords()
        self._radius = radius
        
        self._out_path = pathlib.Path(out_dir)
        self._verbose = verbose
        
        
        self._query_params = self._compute_query_params()
        self._query_name = self._compute_query_name()
        self._filename = self._out_path / (self._query_name + '.xml')
        
        self._stats = QueryStats(self._query_name, self._base_name, 'cone', 
                                 self._access_url, self._query_params, self._result_meta_attrs())
    
    @property 
    def stats(self):
        return self._stats
    
    def run(self):
        response = self.do_query()
        self.stream_to_file(response)
        self.gather_response_metadata(response)
    
    @time_this('do_query')
    def do_query(self):
        response = requests.get(self._access_url, self._query_params, stream=True)
        return response
    
    @time_this('stream_to_file')
    def stream_to_file(self, response):
        with open(self._filename, 'wb+') as fd:
            for chunk in response.iter_content(chunk_size=128):
                fd.write(chunk)   
    
    def _result_meta_attrs(self):
        return ['status', 'size', 'num_rows', 'num_columns']
    
    def gather_response_metadata(self, response):
        result_meta = dict.fromkeys(self._result_meta_attrs())
        result_meta['status'] = response.status_code
        
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                t = Table.read(self._filename, format='votable')
                
            result_meta['size'] = os.path.getsize(self._filename)
            result_meta['num_rows'] = len(t)
            result_meta['num_columns'] = len(t.columns)
        except Exception as e:
            print(value=f'Error reading result table: {e}', file=sys.stderr, flush=True)
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
            raise(ValueError, 'service must have an access_url')
        access_url = html.unescape(access_url)
        return access_url
    
    def _compute_coords(self):
        # Get the RA and Dec from in_coords.
        in_coords = self._orig_coords
        coords = in_coords
        if (type(in_coords) is tuple or type(in_coords) is list) and len(in_coords) == 2:
            coords = SkyCoord(in_coords[0], in_coords[1], frame="icrs", unit="deg")
        elif type(in_coords) is str:
            coords = parse_coordinates(in_coords)
        elif type(in_coords) is not SkyCoord:
            raise ValueError(f"Cannot parse input coordinates {in_coords}")  
        
        return coords
    
    def _compute_query_params(self):
        params = {
            'RA': self._coords.ra.deg,
            'DEC': self._coords.dec.deg,
            'SR': self._orig_radius
        }
        return params
    
    def _compute_query_name(self):
        name = (f'{self._base_name}_{self._service_type}' + 
                f'_{str(self._query_params["RA"])}' +
                f'_{str(self._query_params["DEC"])}' +
                f'_{str(self._query_params["SR"])}')
        return name
    
    def getval(self, obj, key, default=None):
        val = getattr(obj, key, None)
        if val is None:
            val = obj.get(key, default)
        return val     
        




        
        
