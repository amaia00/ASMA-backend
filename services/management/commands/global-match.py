# !/usr/bin/env python3
from django.core.management.base import BaseCommand, CommandError
from services.models import Geonames, ScheduledWork, PENDING, INPROGRESS, FINALIZED, ERROR, \
    SCHEDULED_WORK_CORRESPONDENCE_PROCESS
from datetime import datetime
from django.core.management import call_command
from django.utils import timezone
from django.db import connection

__author__ = 'Amaia Nazabal'


class Command(BaseCommand):
    help = ''

    def handle(self, *args, **options):

            self.stdout.write(
                self.style.MIGRATE_LABEL('%s : The process begins.' %
                                         (datetime.now())))
            scheduled_work = ScheduledWork.objects.get(name=SCHEDULED_WORK_CORRESPONDENCE_PROCESS, status=PENDING)

            # try:
            geoname_entities = Geonames.objects.only('id').filter(correspondence_check=False).values()
            # geonames_entities = Geonames.objects.only('id').filter(correspondence_check=False, latitude__range=(46, 47),
            #                                                       longitude__range=(5, 6)).values()

            # cursor = connection.cursor()
            # cursor.execute("SELECT id FROM services_geonames WHERE FORMAT(latitude, 1) = 45.7  AND FORMAT(longitude, 1) "
            #                "= 4.8")
            # total_rows = len(geonames_entities)
            total_rows = 0
            # geonames_entities = cursor.fetchall()

            '''
            On garde le processus dans la table avec l'état PENDING
            '''
            scheduled_work.status = INPROGRESS
            scheduled_work.total_rows = total_rows
            scheduled_work.initial_date = timezone.now()
            scheduled_work.save()

            for geonames_entity in geoname_entities:
                geonames_entity_id = geonames_entity['id']

                try:
                    call_command('correspondance', geonames_entity_id)

                    scheduled_work.affected_rows += 1
                    scheduled_work.save()

                except Exception as error:
                    scheduled_work.error_rows += 1
                    scheduled_work.save()
                    raise CommandError('%s Error: %s.Entity id %s' %
                                       (datetime.now(), str(error), geonames_entity_id))

            if scheduled_work.error_rows == scheduled_work.affected_rows:
                scheduled_work.status = ERROR
            else:
                scheduled_work.status = FINALIZED

            scheduled_work.final_date = timezone.now()
            scheduled_work.save()

            process_time = scheduled_work.final_date - scheduled_work.initial_date
            self.stdout.write('%s : The process %s ended in %s seconds with %d affected rows and %d '
                              'error rows. Total rows expected %d.' % (datetime.now(), scheduled_work.name,
                                                                       process_time,
                                                                       scheduled_work.affected_rows,
                                                                       scheduled_work.error_rows,
                                                                       scheduled_work.total_rows))
        # except Exception as error:
        #     scheduled_work.status = ERROR
        #     scheduled_work.final_date = timezone.now()
        #     scheduled_work.save()
        #
        #     raise CommandError(error)
