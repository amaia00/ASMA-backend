from gpxpy.geo import haversine_distance
from services.models import Parameters
from services.algorithms.geolocation import GeoLocation

FIRST_LEVEL_PRECISION_MATCH = 5
SECOND_LEVEL_PRECISION_MATCH = 4
THIRD_LEVEL_PRECISION_MATCH = 3
LAST_LEVEL_PRECISION_MATCH = 1


def distance_gps(point1, point2):
    """
    This method return the eucliedien distance between two points 
    :param point1:
    :param point2:
    :return:
    """
    return haversine_distance(point1.get_latitude(), point1.get_longitude(),
                              point2.get_latitude(), point2.get_longitude())


def matching_coordinates(point_reference, point_in_search_ratio, search_ratio=False):
    """
    This méthode calculate the Sim_{coord} of two entities with the eucliedien distance.
    
    :param point_reference: 
    :param point_in_search_ratio: 
    :param search_ratio:
    :return: 
    """
    point1 = GeoLocation.from_degrees(point_reference.get_latitude(), point_reference.get_longitude())
    point2 = GeoLocation.from_degrees(float(point_in_search_ratio.get_latitude()), float(point_in_search_ratio.get_longitude()))

    if not search_ratio:
        search_ratio = float(Parameters.objects.get(name='search_radius_for_blocking').value)
    distance = point1.distance_to(point2)
    matching = 1 - (distance / search_ratio)

    return round(matching, 3)









