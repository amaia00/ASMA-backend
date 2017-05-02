# !/usr/bin/env python3
from django.core.management.base import BaseCommand, CommandError

from services.algorithms.algorithm_learning import LearningAlgorithm
from services.models import ScheduledWork, PENDING, INPROGRESS, FINALIZED, ERROR, \
    SCHEDULED_WORK_LEARNING_ALGORITHM, Parameters
from datetime import datetime
from django.utils import timezone
import numpy as np

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

        error_rates_name = []
        error_rates_type = []
        error_rates_coordinates = []

        try:
            learning_algorithm = LearningAlgorithm()
            for i in range(0, quantity):
                training_set, test_set = learning_algorithm.generate_numpy_array_with_training_and_test_set()

                if DEBUG:
                    print("training set features", training_set[:, :1])
                    print("training set target", training_set[:, 3])

                    print("test set features", test_set[:, :1])
                    print("test set target", test_set[:, 3])

                influence_name = learning_algorithm.get_similarity_attribute_reason(training_set[:, :1],
                                                                                    training_set[:, 3], 'name')

                self.stdout.write(
                    self.style.MIGRATE_HEADING(
                        "%s INFO: Importance name %f" % (datetime.now(), influence_name)))

                error_name_rate = learning_algorithm.validate_attribute_importance(test_set[:, :1], test_set[:, 3],
                                                                                   influence_name, 'name')

                if DEBUG:
                    print("training set features", training_set[:, 1:2])
                    print("training set target", training_set[:, 3])

                    print("test set features", test_set[:, 1:2])
                    print("test set target", test_set[:, 3])

                influence_type = learning_algorithm.get_similarity_attribute_reason(training_set[:, 1:2],
                                                                                    training_set[:, 3], 'type')
                error_type_rate = learning_algorithm.validate_attribute_importance(test_set[:, 1:2], test_set[:, 3],
                                                                                   influence_type, 'type')

                self.stdout.write(
                    self.style.MIGRATE_HEADING(
                        "%s INFO: Importance type %f" % (datetime.now(), influence_type)))

                if DEBUG:
                    print("training set features", training_set[:, 2:3])
                    print("training set target", training_set[:, 3])

                    print("test set features", test_set[:, 2:3])
                    print("test set target", test_set[:, 3])

                influence_coordinates = learning_algorithm.get_similarity_attribute_reason(training_set[:, 2:3],
                                                                                           training_set[:, 3],
                                                                                           'coordinates')
                error_coordinates_rate = learning_algorithm.validate_attribute_importance(test_set[:, 2:3],
                                                                                          test_set[:, 3],
                                                                                          influence_coordinates,
                                                                                          'coordinates')
                weights_name.append(influence_name)
                error_rates_name.append(error_name_rate)
                weights_type.append(influence_type)
                error_rates_type.append(error_type_rate)
                weights_coordinates.append(influence_coordinates)
                error_rates_coordinates.append(error_coordinates_rate)

                self.stdout.write(
                    self.style.MIGRATE_HEADING(
                        "%s INFO: Importance coordinates %f" % (datetime.now(), influence_coordinates)))

            """
            We calculate the average of the values
            """
            weight_name = sum(weights_name) / float(quantity)
            weight_type = sum(weights_type) / float(quantity)
            weight_coordinates = sum(weights_coordinates) / float(quantity)

            self.stdout.write(
                self.style.MIGRATE_HEADING("%s INFO: The average of every attribute is (name, type, coordinates) %f, "
                                           "%f, %f" % (datetime.now(), weight_name, weight_type, weight_coordinates)))

            error_rate_name = sum(error_rates_name) / float(quantity)
            error_rate_type = sum(error_rates_type) / float(quantity)
            error_rate_coordinates = sum(error_rates_coordinates) / float(quantity)

            weights = learning_algorithm.normalize_values(np.array([weight_name, weight_type, weight_coordinates]))

            process_time = timezone.now() - scheduled_work.initial_date

            self.stdout.write('%s : The process %s ended in %s seconds. The estimated weights: (name, type, '
                              'coordinates) are %f, %f, %f.' % (datetime.now(), scheduled_work.name, process_time,
                                                                weights[0], weights[1],
                                                                weights[2]))

            self.stdout.write('%s : The error rates are: (name, type, coordinates) are %f, %f, %f.'
                              % (datetime.now(), error_rate_name, error_rate_type, error_rate_coordinates))

            weights_id = learning_algorithm.save_new_weights(weights[0], weights[1], weights[2])
            affected_rows = 0
            # affected_rows = learning_algorithm.recalculate_pertinence_score(weights_id)

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
