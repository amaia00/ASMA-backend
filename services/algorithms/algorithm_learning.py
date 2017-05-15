from decimal import Decimal

from sklearn.tree import tree
from services.algorithms.pertinence_score import get_pertinence_score_with_weight
from services.models import Parameters, CorrespondenceEntity, ParametersScorePertinence
import numpy as np

DEBUG = False


class LearningAlgorithm:
    def __init__(self):
        """
        Retrieve the data of DB with the defined parameters.
        """
        self.precision = Decimal(Parameters.objects.only('value')
                                 .get(name='precision_of_calculation_of_range_decision_three').value)
        self.iteration = 0
        self.training_set = None
        self.test_set = []

        self.training_set_size = int(Parameters.objects.only('value').get(name='training_set_size_with_test').value)
        self.test_set_size = float(Parameters.objects.only('value').get(name='test_set_percentage').value)

        set_values = CorrespondenceEntity.objects.only('similarity_name', 'similarity_type', 'similarity_coordinates',
                                                       'validation').exclude(validation=0).order_by('?')[
                     :self.training_set_size].all()

        self.training_set_size = len(set_values)
        self.test_set_size = int(self.test_set_size * self.training_set_size)

        list_array = list()
        for correspondence in set_values:
            if int(correspondence.validation) == 1:
                validation = float(1)
            else:
                validation = float(0)

            list_array.append([float(correspondence.similarity_name), float(correspondence.similarity_type),
                               float(correspondence.similarity_coordinates), validation])

        result_array = np.array([row for row in list_array], dtype='f')

        self.division = int(self.training_set_size / self.test_set_size)
        self.results = np.vsplit(result_array, self.division)
        self.universe = result_array

        if DEBUG:
            print("universe", self.universe)

    def generate_numpy_array_with_training_and_test_set(self):
        """
        Take the value of the DB and generate the set for training and test by iteration.
        
        :return: 
        """
        self.test_set = self.results[self.iteration]
        self.training_set = None

        for i in range(0, self.division):
            if i != self.iteration:
                if self.training_set is not None:
                    self.training_set = np.vstack([self.training_set, self.results[i]])
                else:
                    self.training_set = self.results[i]

        self.iteration += 1

        if DEBUG:
            print("iteration", self.iteration)
            print("trainning set", self.training_set)
            print("test set", self.test_set)

        return self.training_set, self.test_set

    def get_similarity_attribute_reason(self, features, target, attribute=''):
        """
        
        :param features: 
        :param target: 
        :param attribute: 
        :return: 
        """
        similarity_attribute = tree.DecisionTreeClassifier()
        similarity_attribute = similarity_attribute.fit(features, target)

        float_values = np.arange(0, 1 + self.precision, self.precision)
        match_times = 0
        total = 0
        for i in float_values:
            t = similarity_attribute.predict([[i]])[0]

            total += 1
            if t == float(1):
                match_times += 1

            if DEBUG:
                print("For similarity {0} {1} classification gives {2}".format(attribute, i, t))

        return match_times / total

    def validate_attribute_importance(self, features, target, importance, attribute=''):
        reason_test = self.get_similarity_attribute_reason(features, target, attribute)
        error_rate = abs(reason_test - importance)
        return error_rate

    @staticmethod
    def save_new_weights(weight_name, weight_type, weight_coordinates):
        """
        
        :param weight_name: 
        :param weight_type: 
        :param weight_coordinates: 
        :return: 
        """
        ParametersScorePertinence.objects.filter(name='weight_matching_global', all_types=1, active=True) \
            .update(active=False)
        params = ParametersScorePertinence(name='weight_matching_global', all_types=1, active=True,
                                           weight_name=weight_name,
                                           weight_type=weight_type, weight_coordinates=weight_coordinates)
        params.save()

        return params.id

    @staticmethod
    def recalculate_pertinence_score(weights_id):
        """
        
        :param weights_id: 
        :return: 
        """
        correspondences = CorrespondenceEntity.objects.only('id').all()
        count = len(correspondences)
        for correspondence_id in correspondences:
            row = CorrespondenceEntity.objects.get(pk=correspondence_id.id)
            _, pertinence_score = get_pertinence_score_with_weight(gn_feature_code=row.gn_feature_code,
                                                                   gn_feature_class=row.gn_feature_class,
                                                                   match_name=row.similarity_name,
                                                                   match_type=row.similarity_type,
                                                                   match_geographical_coordinates=
                                                                   row.similarity_coordinates,
                                                                   weight_id=weights_id)
            row.pertinence_score = pertinence_score
            row.weight_params_id = weights_id
            row.save()

        return count

    @staticmethod
    def normalize_values(array):
        """
        Normalize 3 values between [0, 1]
        :param array: 
        :return: 
        """
        total = sum(array)
        return array[0] / total, array[1] / total, array[2] / total

    @staticmethod
    def soft_max(array):
        """
        Compute softmax values for each sets of scores in x.
        
        The addition between all the elements return 1.
        We can use this function to convert discrete distribution to an uniforme.
        
        Reference: https://en.wikipedia.org/wiki/Softmax_function
        """
        return np.exp(array) / np.sum(np.exp(array), axis=0)

    @staticmethod
    def normalize(array):
        """
        Normalize all the values of array between [0, 1]
        :param array: 
        :return: 
        """
        return array / array.max(axis=0)
