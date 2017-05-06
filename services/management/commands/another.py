from django.db import connection

from services.algorithms.geolocation import GeoLocation
from services.models import Parameters, Node, Tag, Relation, Way, NODE, WAY, RELATION, CorrespondenceEntity
import operator
from util.util import get_name_shape


def get_object_in_ratio(entity, ratio):
    """
    :param entity: the GeoNames entity
    :param ratio: the distance with we going to search others nodes
    :return: the list the nodes wich are in the ratio

    This function returns all the nodes which are in a specific ratio of the entity sended

    Reference: http://janmatuschek.de/LatitudeLongitudeBoundingCoordinates
    """

    loc = GeoLocation.from_degrees(entity.get_position_gps().get_latitude(),
                                   entity.get_position_gps().get_longitude())

    (min_loc, max_loc) = loc.bounding_locations(ratio)
    (lat_min, long_min) = min_loc.get_radians_coordinates()
    (lat_max, long_max) = max_loc.get_radians_coordinates()

    query = "SELECT * FROM TEMP n WHERE RADIANS(lat) >= %(lat_min)s AND RADIANS(lat) <= %(lat_max)s" \
            " AND (RADIANS(n.long) >= %(long_min)s "

    query += "OR " if loc.meridian180_within_distance(ratio) else "AND "

    query += "RADIANS(n.long) <= %(long_max)s) AND ACOS(SIN(%(lat_loc)s) * SIN(RADIANS(lat)) + COS(%(lat_loc)s) * COS(RADIANS(lat))" \
             " * COS(RADIANS(n.long) - %(long_loc)s)) <= %(ang_radius)s"

    lat_loc, long_loc = loc.get_radians_coordinates()
    params = {
        'lat_min': lat_min,
        'long_min': long_min,
        'lat_max': lat_max,
        'long_max': long_max,
        'lat_loc': lat_loc,
        'long_loc': long_loc,
        'ang_radius': loc.get_angular_radius(distance=ratio)
    }

    cursor = connection.cursor()
    query = query % params
    print("Query::: \n", query)
    cursor.execute(query)

    node_list = cursor.fetchall()
    for node in node_list:
        print(node)

