#!/usr/bin/env python3
from django.core.management.base import BaseCommand, CommandError
from services.models import Geoname, CorrespondenceEntity, FeatureCode
from services.classes.classes import EntityGeoNames
from services.algorithms.algorithm_blocking import blocking_function
from services.algorithms.algorithm_align import align_algorithme
from services.algorithms.pertinence_score import get_pertinence_score
from util.util import print_tags

__author__ = 'Amaia Nazabal'


class Command(BaseCommand):
    help = 'This process made the align between entities from GeoNames to OSM.'

    def add_arguments(self, parser):

        parser.add_argument(
            'geoname_id',
            type=int,
            nargs='+',
            help="The geoname id for made the matching with osm entities.")

    def handle(self, geoname_id, *args, **options):
        # try:

            gn_entity = Geoname.objects.get(pk=geoname_id[0])
            entite = EntityGeoNames(id=gn_entity.id, name=gn_entity.name, latitude=gn_entity.latitude,
                                    longitude=gn_entity.longitude, feature_class=gn_entity.fclass,
                                    feature_code=gn_entity.fcode)

            list_block_entities = blocking_function(entite)

            # print("HASTA QUIIIIII----------------------------------------")
            print(list_block_entities)
            # print("HASTA QUIIIIII----------------------------------------")

            list_align_entities = align_algorithme(entite, list_block_entities)

            print("List d'entités alignées")
            print("==========================================================")

            for entity in list_align_entities:
                print("\n")
                print("Entity OSM: ", entity['entity_osm'].id)
                print("----------------------------------------")
                print(entity['entity_osm'])
                print("type_matching", entity['type_matching'])
                print("levenshtein_distance", entity['levenshtein_distance'])

                print("type_tag_osm ", getattr(entity['type_tag_osm'],"key", ''), getattr(entity['type_tag_osm'], 'value', ''))

                print("Tag list")
                print(print_tags(entity['tag_list']))

                pertinence_score = get_pertinence_score(match_name=entity['levenshtein_distance'],
                                                        match_geographical_coordinates=1,
                                                        match_type=entity['type_matching'])

                (latitude_osm, longitude_osm) = entity['coordinates_osm']

                gn_name_type = FeatureCode.objects.filter(code=gn_entity.fclass + '.' + gn_entity.fcode).values('name')[0]['name']
                correspondence = CorrespondenceEntity(reference_gn=gn_entity.id, reference_osm=entity['entity_osm'].id,
                                                      gn_name=gn_entity.name,
                                                      gn_feature_class=gn_entity.fclass,
                                                      gn_feature_code=gn_entity.fcode,
                                                      gn_feature_name=gn_name_type,
                                                      gn_latitude=gn_entity.latitude,
                                                      gn_longitude=gn_entity.longitude,
                                                      osm_name=entity['name_osm'],
                                                      osm_type=entity['shape_osm'],
                                                      osm_key_type=getattr(entity['type_tag_osm'], 'key', ''),
                                                      osm_value_type=getattr(entity['type_tag_osm'], 'value', ''),
                                                      osm_latitude=latitude_osm,
                                                      osm_longitude=longitude_osm,
                                                      name_levenshtein=entity['levenshtein_distance'],
                                                      type_matching=entity['type_matching'],
                                                      pertinence_score=pertinence_score)

                correspondence.save()

        # except Exception as error:
        #     raise CommandError(error)
