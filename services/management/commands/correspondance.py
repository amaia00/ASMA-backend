#!/usr/bin/env python3
from django.core.management.base import BaseCommand, CommandError
from services.models import Geoname, CorrespondenceEntity, FeatureCode, NODE
from services.classes.classes import EntityGeoNames
from services.algorithms.algorithm_blocking import blocking_function
from services.algorithms.algorithm_align import align_algorithme
from services.algorithms.pertinence_score import get_pertinence_score
from services.classes.classes import PositionGPS
from util.util import print_tags
from util.coordinates_matching import matching_coordinates

__author__ = 'Amaia Nazabal'


class Command(BaseCommand):
    help = 'This process made the align between entities from GeoNames to OSM.'

    def add_arguments(self, parser):

        parser.add_argument(
            'geoname_id',
            type=int,
            nargs='+',
            help="The geonanme id for made the matching with osm entities.")

    def handle(self, geoname_id, *args, **options):
        try:
            gn_entity = Geoname.objects.get(pk=geoname_id[0])
            entite = EntityGeoNames(id=gn_entity.id, name=gn_entity.name, latitude=gn_entity.latitude,
                                    longitude=gn_entity.longitude, feature_class=gn_entity.fclass,
                                    feature_code=gn_entity.fcode)

            list_block_entities = blocking_function(entite)
            list_align_entities = align_algorithme(entite, list_block_entities)

            print("List d'entités alignées")
            print("==========================================================")

            for entity in list_align_entities:
                print("\n")
                print("Entity OSM: ", entity['entity_osm'].id)
                print("----------------------------------------")
                print(entity['entity_osm'])
                print("type_matching ", entity['type_matching'])
                print("name_matching ", entity['name_matching'])

                print("type_tag_osm ", getattr(entity['type_tag_osm'], "key", ''),
                      getattr(entity['type_tag_osm'], 'value', ''))

                print("Tag list")
                print(print_tags(entity['tag_list']))

                (latitude_osm, longitude_osm) = entity['coordinates_osm']

                gn_name_type = \
                    FeatureCode.objects.filter(code=gn_entity.fclass + '.' + gn_entity.fcode).values('name')[0]['name']

                position_gn = PositionGPS(gn_entity.latitude, gn_entity.longitude)
                position_osm = PositionGPS(latitude_osm, longitude_osm)
                coordinates_matching = matching_coordinates(position_gn, position_osm)

                pertinence_score = get_pertinence_score(match_name=entity['name_matching'],
                                                        match_geographical_coordinates=coordinates_matching,
                                                        match_type=entity['type_matching'])

                correspondence = CorrespondenceEntity(reference_gn=gn_entity.id, reference_osm=entity['entity_osm'].id,
                                                      gn_name=gn_entity.name,
                                                      gn_feature_class=gn_entity.fclass,
                                                      gn_feature_code=gn_entity.fcode,
                                                      gn_feature_name=gn_name_type,
                                                      gn_latitude=gn_entity.latitude,
                                                      gn_longitude=gn_entity.longitude,
                                                      gn_type=NODE,
                                                      osm_name=entity['name_osm'],
                                                      osm_type=entity['shape_osm'],
                                                      osm_key_type=getattr(entity['type_tag_osm'], 'key', ''),
                                                      osm_value_type=getattr(entity['type_tag_osm'], 'value', ''),
                                                      osm_latitude=latitude_osm,
                                                      osm_longitude=longitude_osm,
                                                      name_matching=entity['name_matching'],
                                                      type_matching=entity['type_matching'],
                                                      coordinates_matching=coordinates_matching,
                                                      pertinence_score=pertinence_score)

                correspondence.save()

        except Exception as error:
            raise CommandError(error)
