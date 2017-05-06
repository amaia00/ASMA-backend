#!/usr/bin/env python3
from django.core.management.base import BaseCommand, CommandError
from services.models import Geonames, CorrespondenceEntity, FeatureCode, NODE
from services.classes.classes import EntityGeoNames
from services.algorithms.algorithm_blocking import blocking_function
from services.algorithms.algorithm_align import align_algorithme
from services.algorithms.pertinence_score import get_pertinence_score
from services.classes.classes import PositionGPS
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

        parser.add_argument(
            '--radium-search',
            default=False,
            metavar="int",
            dest='radium-search',
            help="The search ratio for the blocking")

    def handle(self, geoname_id, *args, **options):
        # try:
            gn_entity = Geonames.objects.get(pk=geoname_id[0])
            entity = EntityGeoNames(id=gn_entity.id, name=gn_entity.name, latitude=gn_entity.latitude,
                                    longitude=gn_entity.longitude, feature_class=gn_entity.fclass,
                                    feature_code=gn_entity.fcode)

            search_ratio = False
            if options.get('radium-search', False):
                search_ratio = float(options['radium-search'])

            list_block_entities = blocking_function(entity, search_ratio)
            list_align_entities = align_algorithme(entity, list_block_entities)
            for entity in list_align_entities:
                (latitude_osm, longitude_osm) = entity['coordinates_osm']

                gn_name_type = \
                    FeatureCode.objects.filter(code=gn_entity.fclass + '.' + gn_entity.fcode).values('name')[0]['name']

                position_gn = PositionGPS(gn_entity.latitude, gn_entity.longitude)
                position_osm = PositionGPS(latitude_osm, longitude_osm)
                coordinates_matching = matching_coordinates(position_gn, position_osm)

                weight_param, pertinence_score = get_pertinence_score(match_name=entity['name_matching'],
                                                                      match_geographical_coordinates=
                                                                      coordinates_matching,
                                                                      match_type=entity['type_matching'],
                                                                      gn_feature_code=gn_entity.fcode,
                                                                      gn_feature_class=gn_entity.fclass)

                correspondence = CorrespondenceEntity(reference_gn=gn_entity.id, reference_osm=entity['entity_osm'].id,
                                                      gn_name=gn_entity.name,
                                                      gn_feature_class=gn_entity.fclass,
                                                      gn_feature_code=gn_entity.fcode,
                                                      gn_feature_name=gn_name_type,
                                                      gn_latitude=gn_entity.latitude,
                                                      gn_longitude=gn_entity.longitude,
                                                      gn_type=NODE,
                                                      osm_name=entity['name_osm'],
                                                      osm_shape=entity['shape_osm'],
                                                      osm_key_type=getattr(entity['type_tag_osm'], 'key', ''),
                                                      osm_value_type=getattr(entity['type_tag_osm'], 'value', ''),
                                                      osm_latitude=latitude_osm,
                                                      osm_longitude=longitude_osm,
                                                      similarity_name=entity['name_matching'],
                                                      similarity_type=entity['type_matching'],
                                                      similarity_coordinates=coordinates_matching,
                                                      pertinence_score=pertinence_score,
                                                      weight_params=weight_param)
                correspondence.save()

            gn_entity.correspondence_check = True
            gn_entity.save()

            print("Quantite de matchs: ", len(list_align_entities))

        # except Exception as error:
        #     raise CommandError(error)
