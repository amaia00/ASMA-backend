from services.models import ParametersScorePertinence


def get_pertinence_score(**kwargs):
    osm_type_key = kwargs.get('osm_type_key')
    osm_type_value = kwargs.get('osm_type_value')

    gn_feature_code = kwargs.get('gn_feature_code')
    gn_feature_class = kwargs.get('gn_feature_class')

    match_name = float(kwargs.get('match_name', 0))
    match_type = float(kwargs.get('match_type', 0))

    match_geographical_coordinates = float(kwargs.get('match_geographical_coordinates', 0))

    all_types = False
    if not osm_type_key:
        all_types = True

    params = ParametersScorePertinence.objects.filter(name='weight_matching',
                                                      osm_key_type=osm_type_key,
                                                      osm_value_type=osm_type_value,
                                                      gn_feature_class=gn_feature_class,
                                                      gn_feature_code=gn_feature_code,
                                                      all_types=all_types).values()[0]

    weight_geographical_coordinates = float(params['weight_coordinates'])
    weight_name_matching = float(params['weight_name'])
    weight_type_matching = float(params['weight_type'])

    match_name_pertinence = match_name * weight_name_matching
    match_type_pertinence = match_type * weight_type_matching
    match_geographical_coordinates_pertinence = match_geographical_coordinates * weight_geographical_coordinates

    return match_name_pertinence + match_type_pertinence + match_geographical_coordinates_pertinence
