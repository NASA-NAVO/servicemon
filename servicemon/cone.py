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
        pass

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

        return {'ra':ra_deg, 'dec':dec_deg}

    @staticmethod
    def random_cone(min_radius, max_radius):
        """
        """
        if not (0 <= min_radius < max_radius):
            raise ValueError('min-radius must be in the range [0,max_radius).')
        coords = Cone.random_coords()
        coords['radius'] = (max_radius - min_radius) * rand() + min_radius
        return coords

    @staticmethod
    def generate_random(num_points, min_radius, max_radius):
        """
        Yield objects with random (and legal) ra, dec, and radius attirbutes.
        """
        if not (0 <= min_radius < max_radius):
            raise ValueError('min-radius must be in the range [0,max_radius).')
        if num_points <= 0:
            raise ValueError('num_point must be a positive number.')

        for i in range(num_points):
            cone = Cone.random_cone(min_radius, max_radius)
            yield cone
