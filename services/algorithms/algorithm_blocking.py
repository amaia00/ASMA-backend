from services.algorithms.geolocation import GeoLocation
from services.models import Parameters, Node, Tag, Relation, Way, NODE, WAY, RELATION, CorrespondenceEntity
import operator
from util.util import get_name_shape


def blocking_function(entite):
    """

    Reference: http://janmatuschek.de/LatitudeLongitudeBoundingCoordinates
    :param entite:
    :return:
    """
    list_match_entities = []
    param_distance_ratio = float(Parameters.objects.get(name='search_radius_for_blocking').value)
    list_entities_in_ratio = get_object_in_ratio(entite, param_distance_ratio)

    for entity_in_ratio in list_entities_in_ratio:
        reference = entity_in_ratio['id']

        entity_osm = Node.objects.filter(pk=reference)

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

        name, is_area = get_name_shape(tag_list)
        if tag_list and name:
            list_match_entities.append({'entity_osm': entity_osm[0],
                                        'name': name,
                                        'shape_osm': is_area or shape_osm,
                                        'coordinates': entity_in_ratio['coordinates'],
                                        'tag_list': tag_list})
        elif not name:
            delete_bd(reference, shape_osm)

    del list_entities_in_ratio
    return list_match_entities


def delete_bd(reference, shape):
    """
    This method delete all the tags and entities without tag name 
    :param reference: 
    :param shape: 
    :return: 
    """
    Tag.objects.filter(reference=reference, type=shape).delete()

    if shape == NODE:
        Node.objects.filter(pk=reference).delete()
    elif shape == WAY:
        nodes = Node.objects.only('id').filter(way_reference__id=reference).values()
        for node in nodes:
            Tag.objects.filter(reference=node['id']).delete()
            Node.objects.filter(pk=node['id']).delete()

    if shape == RELATION:
        delete_relation(reference=reference)


def delete_relation(reference):
    """
    
    :param reference: 
    :return: 
    """
    count = 0
    ways = Way.objects.only('id').filter(relation_reference__id=reference).values()
    for way in ways:
        nodes = Node.objects.only('id').filter(way_reference__id=way['id']).values()
        for node in nodes:
            count += 1
            Tag.objects.filter(reference=node['id']).delete()
            Node.objects.filter(pk=node['id']).delete()

        Tag.objects.filter(reference=way['id']).delete()
        Way.objects.filter(pk=way['id']).delete()

    relations = Relation.objects.only('id').filter(relation_reference__id=reference).values()
    for relation in relations:
        ways = Way.objects.only('id').filter(relation_reference__id=relation['id']).values()
        for way in ways:
            count += 1
            nodes = Node.objects.only('id').filter(way_reference__id=way['id']).values()
            for node in nodes:
                count += 1
                Tag.objects.filter(reference=node['id']).delete()
                Node.objects.filter(pk=node['id']).delete()

            Tag.objects.filter(reference=way['id']).delete()
            Way.objects.filter(pk=way['id']).delete()

        Relation.objects.filter(pk=relation['id']).delete()
        Tag.objects.filter(reference=relation['id']).delete()
    
    print("Tags, nodes, ways and relations deleted", count)


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

    query = "SELECT id FROM services_node n WHERE RADIANS(latitude) >= %(lat_min)s AND RADIANS(latitude) <= " \
            "%(lat_max)s  AND (RADIANS(longitude) >= %(long_min)s "

    query += "OR " if loc.meridian180_within_distance(ratio) else "AND "

    query += "RADIANS(longitude) <= %(long_max)s) AND ACOS(SIN(%(lat_loc)s) * SIN(RADIANS(latitude)) + " \
             "COS(%(lat_loc)s) * COS(RADIANS(latitude)) * COS(RADIANS(longitude) - %(long_loc)s)) <= %(ang_radius)s"

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

    node_list = Node.objects.raw(query, params=params)
    entities_list = []
    for node in node_list:
        point = Node.objects.get(pk=node.id)
        shape = get_parent(node.id, node.way_reference_id, node.relation_reference_id)
        distance = loc.distance_to(GeoLocation.from_degrees(point.latitude, point.longitude))

        try:
            CorrespondenceEntity.objects.only('id').get(reference_gn=entity.get_id(), reference_osm=shape)
        except CorrespondenceEntity.DoesNotExist:
            entities_list.append({
                'id': int(float(shape)),
                'coordinates': (point.latitude, point.longitude),
                'distance': distance
            })

    new_id = None
    coordinates = None
    final_list = []

    entities_list.sort(key=operator.itemgetter('id'))

    """
    We reduce the list for erase entities duplicates
    Control cut
    """
    for entity_l in entities_list:

        (latitude, longitude) = entity_l['coordinates']

        if entity_l['id'] == new_id:
            '''
            If the news coordinates are more closer than the coordinates of the previous point, then we have to replace
            the coordinates and remove the entity of the list, otherwise we ignore the point
            '''
            (lat_before, long_before) = coordinates

            if coordinates and loc.distance_to(GeoLocation.from_degrees(lat_before, long_before)) >= loc.distance_to(
                    GeoLocation.from_degrees(latitude, longitude)):

                final_list.remove({
                    'id': new_id,
                    'coordinates': coordinates
                })
                final_list.append(entity_l)
                coordinates = (latitude, longitude)
                new_id = entity_l['id']
        else:
            '''
            If it's another entity
            '''
            final_list.append(entity_l)

            coordinates = (latitude, longitude)
            new_id = entity_l['id']

    first_fifty = final_list.sort(key=operator.itemgetter('distance'))[:50]
    del entities_list
    del final_list

    return first_fifty


def get_parent(node_id, node_way_reference_id, node_relation_reference_id):
    shape_id = node_id

    try:
        if node_way_reference_id is not None:
            shape_id = node_way_reference_id
            way = Way.objects.only('relation_reference_id').get(pk=node_way_reference_id).relation_reference_id
            node_relation_reference_id = way

        if node_relation_reference_id is not None:
            shape_id = node_relation_reference_id
            relation = Relation.objects.only('relation_reference_id').get(pk=node_relation_reference_id).\
                relation_reference_id

            while relation is not None:
                shape_id = relation
                relation = Relation.objects.only('relation_reference_id').get(pk=shape_id).relation_reference_id

    except (Way.DoesNotExist, Relation.DoesNotExist):
        pass

    return shape_id
