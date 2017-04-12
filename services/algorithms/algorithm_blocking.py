from services.algorithms.geolocation import GeoLocation
from services.models import Parameters, Node, Tag, Relation, Way, NODE, WAY, RELATION


def blocking_function(entite):
    """

    Reference: http://janmatuschek.de/LatitudeLongitudeBoundingCoordinates
    :param entite:
    :return:
    """
    list_match_entities = []
    param_distance_ratio = float(Parameters.objects.get(name='distance_ratio').value)
    shape_list = get_object_in_ratio(entite, param_distance_ratio)

    print("shape list", shape_list)
    for object in shape_list:
        reference = object['id']

        entity_osm = Node.objects.filter(pk=reference).values()

        tag_list = {}
        shape_osm = ''

        """
        Here, we get the tags of every Node or WAY or RELATION
        """
        if entity_osm:
            """
            It's just a node
            """
            tag_list = Tag.objects.filter(reference=reference, type=NODE)
            shape_osm = NODE
        else:
            entity_osm = Relation.objects.filter(pk=reference)

            if entity_osm:
                """
                It's a relation
                """
                tag_list = Tag.objects.filter(reference=reference, type=RELATION)
                shape_osm = RELATION
            else:
                entity_osm = Way.objects.filter(pk=reference)

                if entity_osm:
                    """
                    It's a way
                    """
                    tag_list = Tag.objects.filter(reference=reference, type=WAY)
                    shape_osm = WAY

        if tag_list:
            list_match_entities.append({'entity_osm': entity_osm[0],
                                        'shape_osm': shape_osm,
                                        'coordinates': object['coordinates'],
                                        'tag_list': tag_list})

    print("list tag entities", list_match_entities)

    return list_match_entities


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
    (lat_min, long_min) = min_loc.get_degres_coordinates()
    (lat_max, long_max) = max_loc.get_degres_coordinates()

    query = "SELECT id FROM services_node WHERE latitude >= %(lat_min)s AND latitude <= %(lat_max)s" \
            " AND (longitude >= %(long_min)s "

    query += "OR " if loc.meridian180_within_distance(ratio) else "AND "

    query += "longitude <= %(long_max)s) AND ACOS(SIN(%(lat_loc)s) * SIN(latitude) + COS(%(lat_loc)s) * COS(latitude)" \
             " * COS(longitude - %(long_loc)s)) <= %(ang_radius)s ORDER BY id"

    params = {
        'lat_min': lat_min,
        'long_min': long_min,
        'lat_max': lat_max,
        'long_max': long_max,
        'lat_loc': entity.get_position_gps().get_latitude(),
        'long_loc': entity.get_position_gps().get_longitude(),
        'ang_radius': loc.get_angular_radius(distance=ratio)
    }

    node_list = Node.objects.raw(query, params=params)

    entities_list = []
    for node in node_list:
        point = Node.objects.get(pk=node.id)
        shape = point.way_reference_id or point.relation_reference_id or node.id

        entities_list.append({
            'id': shape,
            'coordinates': (point.latitude, point.longitude)
        })

    id = None
    coordinates = None
    final_list = []

    """
    We reduce the list for erase entities duplicates
    Control cut
    """

    for entity_l in entities_list:

        (latitude, longitude) = entity_l['coordinates']

        if entity_l['id'] == id:
            '''
            If the news coordinates are more closer than the coordinates of the previous point, then we have to replace
            the coordinates and remove the entity of the list, otherwise we ignore the point
            '''
            (lat_before, long_before) = coordinates

            if coordinates and loc.distance_to(GeoLocation.from_degrees(lat_before, long_before)) > loc.distance_to(
                    GeoLocation.from_degrees(latitude, longitude)):

                print("OBJETO QUE QUEREMOS ELIMINAR")
                print({
                    'id': id,
                    'coordinates': coordinates
                })

                final_list.remove({
                    'id': id,
                    'coordinates': coordinates
                })
                final_list.append(entity_l)
        else:
            '''
            If it's another entity
            '''
            final_list.append(entity_l)


        coordinates = (latitude, longitude)
        id = entity_l['id']

    return final_list
