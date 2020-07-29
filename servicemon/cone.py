import os
import sys
import ast
import pprint
from argparse import ArgumentParser

import numpy as np
from numpy.random import random_sample as rand
from astropy import units as u
from astropy.coordinates import SkyCoord


class Cone:
    """
    """

    def __init__(self):
        """
        Not intended to be instantiated.
        """

    @staticmethod
    def random_skycoord():
        """
        """
        ra_rad = (2 * np.pi * rand()) * u.rad
        dec_rad = np.arcsin(2. * (rand() - 0.5)) * u.rad

        skycoord = SkyCoord(ra_rad, dec_rad)
        return skycoord

    @staticmethod
    def random_coords():
        """
        """
        ra_rad = (2 * np.pi * rand()) * u.rad
        ra_deg = ra_rad.to_value(u.deg)
        dec_rad = np.arcsin(2. * (rand() - 0.5)) * u.rad
        dec_deg = dec_rad.to_value(u.deg)

        return {'ra': ra_deg, 'dec': dec_deg}

    @staticmethod
    def random_cone(min_radius, max_radius):
        """
        """
        if not 0 <= min_radius < max_radius:
            raise ValueError('min-radius must be in the range [0,max_radius).')
        coords = Cone.random_coords()
        coords['radius'] = (max_radius - min_radius) * rand() + min_radius
        return coords

    @staticmethod
    def generate_random(num_points, min_radius, max_radius):
        """
        Yield objects with random (and legal) ra, dec, and radius attirbutes.
        """
        if not 0 <= min_radius < max_radius:
            raise ValueError('min-radius must be in the range [0,max_radius).')
        if num_points <= 0:
            raise ValueError('num_points must be a positive number.')

        def cones(num_points, min_radius, max_radius):
            # pylint: disable=unused-variable
            for i in range(num_points):
                cone = Cone.random_cone(min_radius, max_radius)
                yield cone

        return cones(num_points, min_radius, max_radius)

    @staticmethod
    def write_random(num_points, min_radius, max_radius, filename=None):
        generator = Cone.generate_random(num_points, min_radius, max_radius)
        Cone.write_cones(generator, filename)

    @staticmethod
    def write_cones(cones, filename=None):
        stream = sys.stdout
        if filename is not None:
            dirname = os.path.dirname(filename)
            if dirname != '':
                os.makedirs(dirname, exist_ok=True)
            stream = open(filename, "w", encoding="utf-8")

        pp = pprint.PrettyPrinter(width=100, stream=stream, compact=True)
        stream.write("[")
        sep = ''
        indent = '    '
        for cone in cones:
            s = pp.pformat(cone)
            stream.write(f'{sep}\n{indent}{s}')
            sep = ','
        stream.write("\n]\n")

        if filename is not None:
            stream.close()

    @staticmethod
    def reverse_cone_file(infile, outfile=None):
        # read as Python literal
        with open(infile, 'r') as f:
            cones = ast.literal_eval(f.read())

        cones.reverse()

        Cone.write_cones(cones, outfile)


conegen_defaults = {
    'min_radius': 0,
    'max_radius': 0.25
}


def _apply_query_defaults(parsed_args, defaults):
    for k in defaults:
        if getattr(parsed_args, k) is None:
            setattr(parsed_args, k, defaults[k])


def sm_conegen(input_args=None):
    args = _parse_cone_args(input_args)

    Cone.write_random(args.num_cones, args.min_radius, args.max_radius,
                      filename=args.outfile)


def _parse_cone_args(input_args):
    parser = ArgumentParser(description='Generate random cones.')

    parser.add_argument(
        'outfile', help="Name of the output file to contain the cones. ")
    parser.add_argument(
        '--num_cones', type=int, metavar='num_cones', required=True,
        help='Number of cones to generate')
    parser.add_argument(
        '--min_radius', type=float, metavar='min_radius',
        help='Minimum radius (deg).'
        f' Default={conegen_defaults["min_radius"]}')
    parser.add_argument(
        '--max_radius', type=float, metavar='max_radius',
        help='Maximum radius (deg).'
        f' Default={conegen_defaults["max_radius"]}')

    args = parser.parse_args(input_args)

    _apply_query_defaults(args, conegen_defaults)
    return args
