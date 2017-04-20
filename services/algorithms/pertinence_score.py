from services.models import ParametersScorePertinence


def get_pertinence_score(**kwargs):
    osm_type_key = kwargs.get('osm_type_key')
    osm_type_value = kwargs.get('osm_type_value')

    gn_feature_code = kwargs.get('gn_feature_code')
    gn_feature_class = kwargs.get('gn_feature_class')

    match_name = float(kwargs.get('match_name', 0))
    match_type = float(kwargs.get('match_type', 0))

    print("KWARGS MATCH", kwargs.get('match_geographical_coordinates', 0))
    match_geographical_coordinates = float(kwargs.get('match_geographical_coordinates', 0))

    all = False
    if not osm_type_key:
        all = True

    weight_geographical_coordinates = float(
        ParametersScorePertinence.objects.filter(name='weight_geographical_coordinates',
                                                 osm_key_type=osm_type_key,
                                                 osm_value_type=osm_type_value,
                                                 gn_feature_class=gn_feature_class,
                                                 gn_feature_code=gn_feature_code,
                                                 all_types=all).values('value')[0]['value'])

    weight_name_matching = float(ParametersScorePertinence.objects.filter(name='weight_name_matching',
                                                                          osm_key_type=osm_type_key,
                                                                          osm_value_type=osm_type_value,
                                                                          gn_feature_class=gn_feature_class,
                                                                          gn_feature_code=gn_feature_code,
                                                                          all_types=all).values('value')[0]['value'])

    weight_type_matching = float(ParametersScorePertinence.objects.filter(name='weight_name_matching',
                                                                          osm_key_type=osm_type_key,
                                                                          osm_value_type=osm_type_value,
                                                                          gn_feature_class=gn_feature_class,
                                                                          gn_feature_code=gn_feature_code,
                                                                          all_types=all).values('value')[0]['value'])

    print("Poids: ", match_name, match_type)
    match_name_pertinence = match_name * weight_name_matching
    match_type_pertinence = match_type * weight_type_matching
    match_geographical_coordinates_pertinence = match_geographical_coordinates * weight_geographical_coordinates

    return match_name_pertinence + match_type_pertinence + match_geographical_coordinates_pertinence
