from gpxpy.geo import haversine_distance
from decimal import Decimal
from services.models import Parameters


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
    latitude1 = Decimal(point1.get_latitude())
    longitude1 = Decimal(point1.get_longitude())
    latitude2 = Decimal(point2.get_latitude())
    longitude2 = Decimal(point2.get_longitude())

    precision_latitude = min(latitude1.as_tuple().exponent * -1, latitude2.as_tuple().exponent * -1)
    precision_longitude = min(longitude1.as_tuple().exponent * -1, longitude2.as_tuple().exponent * -1)

    matching = 0
    if round(latitude1, precision_latitude) == round(latitude2, precision_latitude) and \
            round(longitude1, precision_longitude) == round(longitude2, precision_longitude):
        matching = Parameters.objects.filter(name='match_coordinates_all_decimals').values('value')[0]['value']
    elif round(latitude1, 4) == round(latitude2, precision_latitude) and \
            round(longitude1, precision_longitude) == round(longitude2, 4):
        matching = Parameters.objects.filter(name='match_coordinates_4_decimals').values('value')[0]['value']
    elif round(latitude1, 3) == round(latitude2, precision_latitude) and \
            round(longitude1, precision_longitude) == round(longitude2, 3):
        matching = Parameters.objects.filter(name='match_coordinates_3_decimals').values('value')[0]['value']
    elif round(latitude1, 1) == round(latitude2, precision_latitude) and \
            round(longitude1, precision_longitude) == round(longitude2, 1):
        matching = Parameters.objects.filter(name='match_coordinates_1_2_decimals').values('value')[0]['value']
    else:
        matching = Parameters.objects.filter(name='match_coordinates_any_decimals').values('value')[0]['value']

    return matching









