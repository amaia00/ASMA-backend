# !/usr/bin/env python3
from django.core.management.base import BaseCommand, CommandError

from services.algorithms.algorithm_learning import LearningAlgorithm
from services.models import Geonames, ScheduledWork, PENDING, INPROGRESS, FINALIZED, ERROR, \
    SCHEDULED_WORK_RECALCULATE_PERTINENCE_SCORE, ParametersScorePertinence
from datetime import datetime
from django.utils import timezone

__author__ = 'Amaia Nazabal'


class Command(BaseCommand):
    help = ''

    def handle(self, *args, **options):

        self.stdout.write(
            self.style.MIGRATE_LABEL('%s : The process begins.' %
                                     (datetime.now())))
        scheduled_work = ScheduledWork.objects.get(name=SCHEDULED_WORK_RECALCULATE_PERTINENCE_SCORE, status=PENDING)

        try:
            geoname_entities = Geonames.objects.only('id').filter(correspondence_check=False).values()
            total_rows = len(geoname_entities)

            '''
            On garde le processus dans la table avec l'état PENDING
            '''
            scheduled_work.status = INPROGRESS
            scheduled_work.total_rows = total_rows
            scheduled_work.initial_date = timezone.now()
            scheduled_work.save()

            weights_id = int(ParametersScorePertinence.objects.get(name="weight_matching_global", active=1, all_types=1).id)
            affected_rows = LearningAlgorithm.recalculate_pertinence_score(weights_id)

            if scheduled_work.error_rows == scheduled_work.affected_rows:
                scheduled_work.status = ERROR
            else:
                scheduled_work.status = FINALIZED

            scheduled_work.affected_rows = affected_rows
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
            scheduled_work.status = ERROR
            scheduled_work.final_date = timezone.now()
            scheduled_work.save()

            raise CommandError(error)
