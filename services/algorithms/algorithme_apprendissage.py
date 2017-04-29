from services.models import Parameters, CorrespondenceValide, CorrespondenceInvalide, FeatureCode
from django.db.models import Avg, Min, Max


def threshold_calculation_similarity_name():
    average = CorrespondenceValide.objects.aggregate(Avg('similarity_name'))
    min = CorrespondenceValide.objects.aggregate(Min('similarity_name'))
    max = CorrespondenceValide.objects.aggregate(Max('similarity_name'))

    return min, average, max


def threshold_calculation_similarity_type():
    average = CorrespondenceValide.objects.aggregate(Avg('similarity_type'))
    min = CorrespondenceValide.objects.aggregate(Min('similarity_type'))
    max = CorrespondenceValide.objects.aggregate(Max('similarity_type'))

    return min, average, max


def threshold_calculation_similarity_coordinates():
    average = CorrespondenceValide.objects.aggregate(Avg('similarity_coordinates'))
    min = CorrespondenceValide.objects.aggregate(Min('similarity_coordinates'))
    max = CorrespondenceValide.objects.aggregate(Max('similarity_coordinates'))

    return min, average, max
