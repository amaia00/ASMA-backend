# !/usr/bin/env python3
from django.core.management.base import BaseCommand, CommandError
from services.models import Geoname, ScheduledWork, PENDING, INPROGRESS, FINALIZED, ERROR
from datetime import datetime
from django.core.management import call_command
from django.utils import timezone

__author__ = 'Amaia Nazabal'


class Command(BaseCommand):
    help = ''

    def handle(self, *args, **options):

        self.stdout.write(
            self.style.MIGRATE_LABEL('%s : The process begins.' %
                                     (datetime.now())))
        try:
            # TODO correspondence_check=False
            geoname_entities = Geoname.objects.only('id').filter(correspondence_check=False).values()
            total_rows = geoname_entities.count()

            '''
            On garde le processus dans la table avec l'état PENDING
            '''
            scheduled_work = ScheduledWork.objects.get(name='correspondence_process', status=PENDING)
            scheduled_work.status = INPROGRESS
            scheduled_work.total_rows = total_rows
            scheduled_work.initial_date = timezone.now()
            scheduled_work.save()

            for geoname_entity in geoname_entities:
                try:
                    call_command('correspondance', geoname_entity['id'])

                    scheduled_work.affected_rows += 1
                    scheduled_work.save()

                except CommandError as error:
                    self.stdout.write(
                        self.style.ERROR('%s :Error: %s.' %
                                                 (datetime.now(), error)))
                    scheduled_work.error_rows += 1
                    scheduled_work.save()

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
        except Exception as error:
            raise CommandError(error)
