# !/usr/bin/env python3
from django.core.management.base import BaseCommand, CommandError
from services.classes.classes import PositionGPS
from util.coordinates_matching import matching_coordinates
from services.models import CorrespondenceTypes, CorrespondenceTypesClose
from decimal import *

__author__ = 'Amaia Nazabal'


class Command(BaseCommand):
    help = 'This service allows import all the correspondences between types with a criteria related to the quantity' \
           ' of people how made the correspondences.'

    def handle(self, *args, **options):

        # try:

            position_gn = PositionGPS(Decimal(42.5116200), Decimal(1.5340800))
            position_osm = PositionGPS(Decimal(42.5114983), Decimal(1.5344814))

            coordinates_matching = matching_coordinates(position_gn, position_osm)
            print(coordinates_matching)

        # except Exception as error:
        #     raise CommandError(error)
