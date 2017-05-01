from decimal import Decimal
from sklearn.tree import tree

from services.algorithms.pertinence_score import get_pertinence_score_with_weight
from services.models import Parameters, CorrespondenceEntity, ParametersScorePertinence
import numpy as np
from util.util import split_array

DEBUG = False


def generate_numpy_array_with_training_set():
    training_set_size = int(Parameters.objects.only('value').get(name='training_set_size').value)
    set_values = CorrespondenceEntity.objects.only('similarity_name', 'similarity_type', 'similarity_coordinates',
                                                   'validation').exclude(validation=0).order_by('?')[
                 :training_set_size].all()

    list_array = list()
    for correspondence in set_values:
        if int(correspondence.validation) == 1:
            validation = float(1)
        else:
            validation = float(0)

        list_array.append([float(correspondence.similarity_name), float(correspondence.similarity_type),
                           float(correspondence.similarity_coordinates), validation])

    result_array = np.array([row for row in list_array])
    return result_array


def get_test_set():
    test_set = int(Parameters.objects.only('value').get(name='test_set_size').value)
    set_values = CorrespondenceEntity.objects.only('similarity_name', 'similarity_type', 'similarity_coordinates',
                                                   'validation').exclude(validation=0).order_by('?')[:test_set].all()
    return set_values


def get_similarity_attribute_reason(test_set, attribute, range_minimum, range_maximum):
    qte_total = len(test_set)
    qte_match_in_range = 0
    for test in test_set:
        if test.validation == 1 and range_minimum <= float(getattr(test, attribute)) <= range_maximum:
            qte_match_in_range += 1

    return qte_match_in_range / qte_total


def get_range_values(features, target, attribute=''):
    similarity_attribute = tree.DecisionTreeClassifier(random_state=0)
    similarity_attribute = similarity_attribute.fit(features, target)
    precision = Decimal(Parameters.objects.only('value').get(name='precision_of_calculation_of_range_decision_three')
                      .value)

    float_values = np.arange(0, 1 + precision, precision)
    range_attribute = []
    for i in float_values:
        another = i
        t = similarity_attribute.predict([[i]])[0]

        if t == float(1):
            range_attribute.append(float(str(another)))

        if DEBUG:
            print("For similarity {0} {1} classification gives {2}".format(attribute, i, t))

    ranges_attribute = split_array(range_attribute, precision)

    if DEBUG:
        print("All ranges {0}".format(attribute), ranges_attribute)

    max_elements = 0
    max_range_attribute = []
    for range in ranges_attribute:
        if len(range) >= max_elements:
            max_range_attribute = range
            max_elements = len(range)

    if not max_range_attribute:
        return 0, 0

    if DEBUG:
        print("Range {0}:".format(attribute), max_range_attribute[0], "-", max_range_attribute[-1])

    return max_range_attribute[0], max_range_attribute[-1]


def save_new_weights(weight_name, weight_type, weight_coordinates):
    ParametersScorePertinence.objects.filter(name='weight_matching_global', all_types=1, active=True) \
        .update(active=False)
    params = ParametersScorePertinence(name='weight_matching_global', all_types=1, active=True, weight_name=weight_name,
                                       weight_type=weight_type, weight_coordinates=weight_coordinates)
    params.save()

    return params.id


def recalculate_pertinence_score(weights_id):
    correspondences = CorrespondenceEntity.objects.only('id').all()
    count = len(correspondences)
    for correspondence_id in correspondences:
        row = CorrespondenceEntity.objects.get(pk=correspondence_id.id)
        _, pertinence_score = get_pertinence_score_with_weight(gn_feature_code=row.gn_feature_code,
                                                               gn_feature_class=row.gn_feature_class,
                                                               match_name=row.similarity_name,
                                                               match_type=row.similarity_type,
                                                               match_geographical_coordinates=row.similarity_coordinates,
                                                               weight_id=weights_id)
        row.pertinence_score = pertinence_score
        row.weight_params_id = weights_id
        row.save()

    return count


def normalize_values(weight_name, weight_type, weight_coordinates):
    total = weight_name + weight_type + weight_coordinates
    return weight_name/total, weight_type/total, weight_coordinates/total