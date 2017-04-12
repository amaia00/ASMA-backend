from gpxpy.geo import haversine_distance


def distance_gps(point1, point2):
    """

    :param point1:
    :param point2:
    :return:
    """
    return haversine_distance(point1.get_latitude(), point1.get_longitude(),
                              point2.get_latitude(), point2.get_longitude())

