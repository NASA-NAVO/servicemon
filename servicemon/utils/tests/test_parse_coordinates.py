import pytest

import astropy.coordinates as coord
import astropy.units as u

from ...utils import parse_coordinates


@pytest.mark.parametrize(('coordinates'),
                         [coord.SkyCoord(ra=148, dec=69, unit=(u.deg, u.deg)),
                          ]
                         )
def test_parse_coordinates_1(coordinates):
    c = parse_coordinates(coordinates)
    assert c is not None


@pytest.mark.remote_data
@pytest.mark.parametrize(('coordinates'),
                         ["00h42m44.3s +41d16m9s",
                          "m81"])
def test_parse_coordinates_2(coordinates):
    c = parse_coordinates(coordinates)
    assert c is not None


def test_parse_coordinates_3():
    with pytest.raises(Exception):
        parse_coordinates(9.8 * u.kg)


def test_parse_coordinates_4():
    # Regression test for #1251
    coordinates = "251.51 32.36"
    c = parse_coordinates(coordinates)
    assert c.to_string() == coordinates
