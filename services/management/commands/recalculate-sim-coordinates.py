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

    def handle(self, *args, **options):
        try:
            correspondences = CorrespondenceEntity.objects.only('id', 'reference_gn', 'osm_latitude', 'osm_longitude')\
                .all()
            for correspondence in correspondences:
                gn_entity = Geonames.objects.only('latitude', 'longitude').get(pk=correspondence.reference_gn)

                position_gn = PositionGPS(gn_entity.latitude, gn_entity.longitude)
                position_osm = PositionGPS(correspondence.osm_latitude, correspondence.osm_longitude)
                coordinates_matching = matching_coordinates(position_gn, position_osm, 1)
                CorrespondenceEntity.objects.filter(pk=correspondence.id).update(
                    similarity_coordinates=coordinates_matching)

        except Exception as error:
            raise CommandError(error)
