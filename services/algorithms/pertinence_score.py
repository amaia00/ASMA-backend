from services.models import ParametersScorePertinence


def get_pertinence_score(**kwargs):
    """
    This method determines the global score according to the weights of every attribute
    
    :param kwargs: 
    :return: 
    """
    gn_feature_code = kwargs.get('gn_feature_code')
    gn_feature_class = kwargs.get('gn_feature_class')

    match_name = float(kwargs.get('match_name', 0))
    match_type = float(kwargs.get('match_type', 0))

    match_geographical_coordinates = float(kwargs.get('match_geographical_coordinates', 0))

    try:
        params = ParametersScorePertinence.objects.get(name='weight_matching',
                                                       gn_feature_code=gn_feature_code,
                                                       gn_feature_class=gn_feature_class,
                                                       all_types=False,
                                                       active=True)
    except ParametersScorePertinence.DoesNotExist:
        params = ParametersScorePertinence.objects.get(name='weight_matching_global',
                                                       all_types=True, active=True)

    weight_geographical_coordinates = float(params.weight_coordinates)
    weight_name_matching = float(params.weight_name)
    weight_type_matching = float(params.weight_type)

    match_name_pertinence = match_name * weight_name_matching
    match_type_pertinence = match_type * weight_type_matching
    match_geographical_coordinates_pertinence = match_geographical_coordinates * weight_geographical_coordinates

    return params, match_name_pertinence + match_type_pertinence + match_geographical_coordinates_pertinence


def get_pertinence_score_with_weight(**kwargs):
    """
    The same method as above, but we can send it the id of the weights
    :param kwargs: 
    :return: 
    """
    gn_feature_code = kwargs.get('gn_feature_code')
    gn_feature_class = kwargs.get('gn_feature_class')

    match_name = float(kwargs.get('match_name', 0))
    match_type = float(kwargs.get('match_type', 0))
    match_geographical_coordinates = float(kwargs.get('match_geographical_coordinates', 0))

    weight_id = int(kwargs.get('weight_id', 0))

    try:
        params = ParametersScorePertinence.objects.get(name='weight_matching',
                                                       gn_feature_code=gn_feature_code,
                                                       gn_feature_class=gn_feature_class,
                                                       all_types=False,
                                                       active=True)
    except ParametersScorePertinence.DoesNotExist:
        params = ParametersScorePertinence.objects.get(pk=weight_id)

    weight_geographical_coordinates = float(params.weight_coordinates)
    weight_name_matching = float(params.weight_name)
    weight_type_matching = float(params.weight_type)

    match_name_pertinence = match_name * weight_name_matching
    match_type_pertinence = match_type * weight_type_matching
    match_geographical_coordinates_pertinence = match_geographical_coordinates * weight_geographical_coordinates

    return params, match_name_pertinence + match_type_pertinence + match_geographical_coordinates_pertinence
