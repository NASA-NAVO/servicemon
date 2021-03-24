# Licensed under a 3-clause BSD style license - see LICENSE.rst
"""
This parse_coordinates method is adapted from an Astroquery utility method of
the same name (see https://github.com/astropy/astroquery/blob/master/astroquery/utils/commons.py)
which is also under a 3-clause BSD style license.

This adaptation is just to avoid a dependency on Astroquery.
"""

import warnings
import astropy.units as u
from astropy import coordinates as coord

from astropy.coordinates import BaseCoordinateFrame


def ICRSCoordGenerator(*args, **kwargs):
    return coord.SkyCoord(*args, frame='icrs', **kwargs)


ICRSCoord = coord.SkyCoord
CoordClasses = (coord.SkyCoord, BaseCoordinateFrame)


__all__ = ['parse_coordinates']


def parse_coordinates(coordinates):
    """
    Takes a string or astropy.coordinates object. Checks if the
    string is parsable as an `astropy.coordinates`
    object or is a name that is resolvable. Otherwise asserts
    that the argument is an astropy.coordinates object.

    Parameters
    ----------
    coordinates : str or `astropy.coordinates` object
        Astronomical coordinate

    Returns
    -------
    coordinates : a subclass of `astropy.coordinates.BaseCoordinateFrame`


    Raises
    ------
    astropy.units.UnitsError
    TypeError
    """
    if isinstance(coordinates, str):
        try:
            c = ICRSCoordGenerator(coordinates)
            warnings.warn("Coordinate string is being interpreted as an "
                          "ICRS coordinate.")

        except u.UnitsError:
            warnings.warn("Only ICRS coordinates can be entered as "
                          "strings.\n For other systems please use the "
                          "appropriate astropy.coordinates object.")
            raise u.UnitsError
        except ValueError as err:
            if isinstance(err.args[1], u.UnitsError):
                try:
                    c = ICRSCoordGenerator(coordinates, unit='deg')
                    warnings.warn("Coordinate string is being interpreted as an "
                                  "ICRS coordinate provided in degrees.")

                except ValueError:
                    c = ICRSCoord.from_name(coordinates)
            else:
                c = ICRSCoord.from_name(coordinates)

    elif isinstance(coordinates, CoordClasses):
        if hasattr(coordinates, 'frame'):
            c = coordinates
        else:
            # Convert the "frame" object into a SkyCoord
            c = coord.SkyCoord(coordinates)
    else:
        raise TypeError("Argument cannot be parsed as a coordinate")
    return c
