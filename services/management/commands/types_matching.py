
#TODO: Add the algorithme for retrieved the types correspondences,
#We have to add a parameter for decide if we have a specfied quantity of match y one type, we have to
#add in the correspondence type table.

#!/usr/bin/env python3
from django.core.management.base import BaseCommand, CommandError
from services.algorithms.geolocation import GeoLocation
from services.models import Geoname, CorrespondenceEntity, Node
from services.classes.classes import EntityGeoNames
from services.algorithms.algorithm_blocking import blocking_function
from services.algorithms.algorithm_align import align_algorithme
from services.algorithms.pertinence_score import get_pertinence_score
from util.util import print_tags

__author__ = 'Amaia Nazabal'


class Command(BaseCommand):
    help = '.'
    #
    # def add_arguments(self, parser):
    #
    #     parser.add_argument(
    #         'geoname_id',
    #         type=int,
    #         nargs='+',
    #         help="The geoname id for made the matching with osm entities.")

    def handle(self, *args, **options):
        try:
            print("The process begin")
            gn = Geoname.objects.get(pk=3041471)
            point1 = GeoLocation.from_degrees(gn.latitude, gn.longitude)

            osm = Node.objects.get(pk=1933977604)
            point2 = GeoLocation.from_degrees(osm.latitude, gn.longitude)

            distance = point1.distance_to(point2)

            print("Distance:::")
            print(distance)


        except Exception as error:
            raise CommandError(error)


