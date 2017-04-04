from services.models import Parameters


def get_pertinence_score(match_name, match_type, match_geographical_coordinates):
    weight_geographical_coordinates = float(Parameters.objects.get(name='weight_geographical_coordinates').value)
    weight_name_matching = float(Parameters.objects.get(name='weight_name_matching').value)
    weight_type_matching = float(Parameters.objects.get(name='weight_type_matching').value)

    match_name_pertinence = match_name * weight_name_matching
    match_type_pertinence = match_type * weight_type_matching
    match_geographical_coordinates_pertinence = match_geographical_coordinates * weight_geographical_coordinates

    return match_name_pertinence + match_type_pertinence + match_geographical_coordinates_pertinence
