from gpxpy.geo import haversine_distance
from decimal import Decimal
from services.models import Parameters

FIRST_LEVEL_PRECISION_MATCH = 5
SECOND_LEVEL_PRECISION_MATCH = 4
THIRD_LEVEL_PRECISION_MATCH = 3
LAST_LEVEL_PRECISION_MATCH = 1


def distance_gps(point1, point2):
    """

    :param point1:
    :param point2:
    :return:
    """
    return haversine_distance(point1.get_latitude(), point1.get_longitude(),
                              point2.get_latitude(), point2.get_longitude())


def matching_coordinates(point1, point2):
    """
    
    :param point1: 
    :param point2: 
    :return: 
    """
    latitude1 = point1.get_latitude()
    longitude1 = Decimal(point1.get_longitude())
    latitude2 = Decimal(point2.get_latitude())
    longitude2 = Decimal(point2.get_longitude())

    if round(latitude1, FIRST_LEVEL_PRECISION_MATCH) == round(latitude2, FIRST_LEVEL_PRECISION_MATCH) and \
            round(longitude1, FIRST_LEVEL_PRECISION_MATCH) == round(longitude2, FIRST_LEVEL_PRECISION_MATCH):

        matching = Parameters.objects.filter(name='match_coordinates_all_decimals').values('value')[0]['value']

    elif round(latitude1, SECOND_LEVEL_PRECISION_MATCH) == round(latitude2, SECOND_LEVEL_PRECISION_MATCH) and \
            round(longitude1, SECOND_LEVEL_PRECISION_MATCH) == round(longitude2, SECOND_LEVEL_PRECISION_MATCH):

        matching = Parameters.objects.filter(name='match_coordinates_4_decimals').values('value')[0]['value']

    elif round(latitude1, THIRD_LEVEL_PRECISION_MATCH) == round(latitude2, THIRD_LEVEL_PRECISION_MATCH) and \
            round(longitude1, THIRD_LEVEL_PRECISION_MATCH) == round(longitude2, THIRD_LEVEL_PRECISION_MATCH):

        matching = Parameters.objects.filter(name='match_coordinates_3_decimals').values('value')[0]['value']

    elif round(latitude1, LAST_LEVEL_PRECISION_MATCH) == round(latitude2, LAST_LEVEL_PRECISION_MATCH) and \
            round(longitude1, LAST_LEVEL_PRECISION_MATCH) == round(longitude2, LAST_LEVEL_PRECISION_MATCH):

        matching = Parameters.objects.filter(name='match_coordinates_1_2_decimals').values('value')[0]['value']

    else:
        matching = Parameters.objects.filter(name='match_coordinates_any_decimals').values('value')[0]['value']

    return matching









