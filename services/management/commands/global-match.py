
# !/usr/bin/env python3
from django.core.management.base import BaseCommand, CommandError
from services.models import Geoname
from datetime import datetime
from services.management.commands.correspondance import Command

__author__ = 'Amaia Nazabal'


class Command(BaseCommand):
    help = ''

    def handle(self, *args, **options):

        self.stdout.write(
            self.style.MIGRATE_LABEL('%s : The process begins.' %
                                     (datetime.now())))
        try:
            # TODO correspondence_check=False
            geoname_entities = Geoname.objects.only('id').filter(correspondence_check=True).values()

            for geoname_entity in geoname_entities:
                Command.handle(geoname_id=geoname_entity.id)

            self.stdout.write(
                self.style.MIGRATE_HEADING('%s : Correspondences in the set of correspondences valides.' %
                                           (datetime.now())))

            self.stdout.write(
                self.style.SUCCESS('%s : The process ended with %s new correspondences in the close set.' %
                                   (datetime.now(), str(len(all)))))

        except Exception as error:
            raise CommandError(error)
