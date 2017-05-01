# !/usr/bin/env python3
from django.core.management.base import BaseCommand, CommandError

from services.algorithms.algorithm_learning import generate_numpy_array_with_training_set, get_test_set, \
    get_range_values, get_similarity_attribute_reason, save_new_weights, recalculate_pertinence_score, normalize_values
from services.models import ScheduledWork, PENDING, INPROGRESS, FINALIZED, ERROR, \
    SCHEDULED_WORK_LEARNING_ALGORITHM, Parameters
from datetime import datetime
from django.utils import timezone

DEBUG = False
__author__ = 'Amaia Nazabal'


class Command(BaseCommand):
    help = 'The learning algorithm for calculate the weights of the similarity attributes'

    def handle(self, *args, **options):

        self.stdout.write(
            self.style.MIGRATE_LABEL('%s : The process begins.' %
                                     (datetime.now())))

        '''
        On garde le processus dans la table avec l'état PENDING
        '''
        scheduled_work = ScheduledWork.objects.get(name=SCHEDULED_WORK_LEARNING_ALGORITHM, status=PENDING)
        scheduled_work.status = INPROGRESS
        scheduled_work.initial_date = timezone.now()
        scheduled_work.save()

        quantity = int(Parameters.objects.only('value').get(name='times_of_execution_learning_algorithm').value)

        weights_name = []
        weights_type = []
        weights_coordinates = []

        try:

            for i in range(0, quantity):
                training_set = generate_numpy_array_with_training_set()

                if DEBUG:
                    print("features", training_set[:, :1])
                    print("target", training_set[:, 3])

                range_min_name, range_max_name = get_range_values(training_set[:, :1], training_set[:, 3], 'name')
                self.stdout.write(
                    self.style.MIGRATE_HEADING(
                        "%s INFO: Attribute name range [%f - %f]" % (datetime.now(), range_min_name,
                                                                     range_max_name)))

                if DEBUG:
                    print("features", training_set[:, 1:2])
                    print("target", training_set[:, 3])

                range_min_type, range_max_type = get_range_values(training_set[:, 1:2], training_set[:, 3], 'type')

                self.stdout.write(
                    self.style.MIGRATE_HEADING(
                        "%s INFO: Attribute type range [%f - %f]" % (datetime.now(), range_min_type,
                                                                     range_max_type)))

                if DEBUG:
                    print("features", training_set[:, 2:3])
                    print("target", training_set[:, 3])

                range_min_coordinates, range_max_coordinates = get_range_values(training_set[:, 2:3],
                                                                                training_set[:, 3], 'coordinates')

                self.stdout.write(
                    self.style.MIGRATE_HEADING("%s INFO: Attribute coordinates range [%f - %f]" % (datetime.now(),
                                                                                                   range_min_coordinates,
                                                                                                   range_max_coordinates)))

                test_set = get_test_set()
                reason_name = round(get_similarity_attribute_reason(test_set, 'similarity_name', range_min_name,
                                                                    range_max_name), 2)
                reason_type = round(get_similarity_attribute_reason(test_set, 'similarity_type', range_min_type,
                                                                    range_max_type), 2)
                reason_coordinates = round(get_similarity_attribute_reason(test_set, 'similarity_coordinates',
                                                                           range_min_coordinates,
                                                                           range_max_coordinates), 2)

                weight_name, weight_type, weight_coordinates = normalize_values(reason_name, reason_type,
                                                                                reason_coordinates)

                weights_name.append(weight_name)
                weights_type.append(weight_type)
                weights_coordinates.append(weight_coordinates)

            """
            We calculate the average of the values
            """
            weight_name = sum(weights_name) / quantity
            weight_type = sum(weights_type) / quantity
            weight_coordinates = sum(weights_coordinates) / quantity

            weight_name, weight_type, weight_coordinates = normalize_values(weight_name, weight_type,
                                                                            weight_coordinates)
            process_time = timezone.now() - scheduled_work.initial_date
            self.stdout.write('%s : The process %s ended in %s seconds. The estimated weights: (name, type, '
                              'coordinates) are %f, %f, %f.' % (datetime.now(), scheduled_work.name, process_time,
                                                                weight_name, weight_type, weight_coordinates))

            weights_id = save_new_weights(weight_name, weight_type, weight_coordinates)
            affected_rows = recalculate_pertinence_score(weights_id)

            scheduled_work.status = FINALIZED
            scheduled_work.final_date = timezone.now()
            scheduled_work.affected_rows = affected_rows
            scheduled_work.save()

            self.stdout.write('%s : The process for recalculate the pertinence score ended. Affected rows: %d'
                              % (datetime.now(), affected_rows))

        except Exception as error:
            scheduled_work.status = ERROR
            scheduled_work.final_date = timezone.now()
            scheduled_work.save()
            raise CommandError(error)
