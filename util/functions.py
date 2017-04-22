from services.models import Node, Way, Relation, NODE, RELATION, AREA, WAY


def update_correspondence_osm(osm_id, shape):
    if shape == NODE:
        Node.objects.filter(id=osm_id).update(check_name=True)
    elif shape == RELATION:
        Relation.objects.filter(id=osm_id).update(check_name=True)
    else:
        Way.objects.filter(id=osm_id).update(check_name=True)
