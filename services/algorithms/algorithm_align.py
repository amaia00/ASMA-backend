import json
import requests

from services.models import Parameters, CorrespondenceTypes, CorrespondenceTypesClose, FeatureCode, \
    CorrespondenceTypesInvalid
from util.string_matching import distance_levenshtein
from util.util import get_name_shape, remove_tag_name, print_tags


def align_algorithme(entity_gn, list_block_osm_entities):
    """

    :param entity_gn:
    :param list_block_osm_entities: avec tag list
    :return:
    """

    list_aligned_entities = []

    for entity_osm in list_block_osm_entities:

        matching_name_level = match_name_string(entity_gn, entity_osm.get('name'))

        type_tag_osm, matching_type_level = match_type_correspondence(entity_gn, entity_osm.get('tag_list'))
        if not type_tag_osm:
            type_tag_osm, matching_type_level = match_type_synonyms(entity_gn, entity_osm.get('tag_list'))

        """
        We add to the matched entities list the entities which a level of matching with
        the name and type matching
        """
        list_aligned_entities.append({
            'name_osm': entity_osm.get('name'),
            'shape_osm': entity_osm.get('shape_osm'),
            'entity_osm': entity_osm.get('entity_osm'),
            'coordinates_osm': entity_osm.get('coordinates'),
            'tag_list': entity_osm.get('tag_list'),
            'name_matching': matching_name_level,
            'type_matching': matching_type_level,
            'type_tag_osm': type_tag_osm
        })

    return list_aligned_entities


def match_name_string(entity_gn, osm_name):
    """
    We calculate the levenshtein distance between the osm_name and geonames' names

    :param entity_gn:
    :param osm_name:
    :return: the level of matching if it is greater or equals to the parameter, otherwise False
    """
    param_distance_string = float(Parameters.objects.get(name='minimun_similarity_name_for_align').value)

    value = distance_levenshtein(entity_gn.get_name(), osm_name)
    if value >= param_distance_string:
        return value

    return False


def match_type_correspondence(entity_gn, tag_list):
    """
    This methode check if the type has a entier correspondance with every tag of the object
    :param entity_gn:
    :param tag_list:
    :return:
    """
    match_level = 0
    tag_match = False

    similarity_type_for_total_match = float(Parameters.objects.get(name="similarity_type_for_total_match").value)
    similarity_type_for_users_validation = float(Parameters.objects.get(name="similarity_type_for_users_validation")
                                                 .value)

    tag_list = remove_tag_name(tag_list)
    for tag in tag_list:
        match = CorrespondenceTypes.objects.filter(gn_feature_code=entity_gn.get_feature_code(),
                                                   gn_feature_class=entity_gn.get_feature_class(),
                                                   osm_key=tag.key,
                                                   osm_value=tag.value).count()

        if match > 0:
            return tag, similarity_type_for_total_match

        match_close = CorrespondenceTypesClose.objects.filter(gn_feature_code=entity_gn.get_feature_code(),
                                                              gn_feature_class=entity_gn.get_feature_class(),
                                                              osm_key=tag.key,
                                                              osm_value=tag.value).count()

        if match_close > 0 and max(similarity_type_for_users_validation, match_level) != match_level:
            (tag_match, match_level) = (tag, max(similarity_type_for_users_validation, match_level))

        match_invalid = CorrespondenceTypesInvalid.objects.filter(gn_feature_code=entity_gn.get_feature_code(),
                                                                  gn_feature_class=entity_gn.get_feature_class(),
                                                                  osm_key=tag.key,
                                                                  osm_value=tag.value, active=True).count()

        if match_invalid > 0 and match_level == 0:
            (tag_match, match_level) = (tag, 0)

    return tag_match, match_level


def match_type_synonyms(entity_gn, tag_list):
    """
    This method is called if we don't find a match between the object and the entier list of tags,
    so here we use the synonyms service for find a match.

    We search synonyms with the marshape api urban
    Reference: https://market.mashape.com/community/urban-dictionary

    :param entity_gn:
    :param tag_list:
    :return:
    """

    feature_code = FeatureCode.objects.get(code=entity_gn.get_feature_class() + '.' + entity_gn.get_feature_code())

    param_api_url = Parameters.objects.get(name='api_synonyms_url').value
    param_api_hash_key = Parameters.objects.get(name='api_synonyms_hash_key').value
    param_api_hash_value = Parameters.objects.get(name='api_synonyms_hash_value').value

    synonyms = []
    try:
        if feature_code.name != 'fourth-order administrative division':
            r = requests.get(param_api_url + feature_code.name,
                             headers={param_api_hash_key: param_api_hash_value})

            json_object = json.loads(r.text)
            synonyms = json_object["tags"]
    except Exception as error:
        print("Error synonyms service" + str(error))

    similarity_type_level = 0
    tag_match = ''

    similarity_type_for_description_in_key = float(Parameters.objects
                                                   .get(name="similarity_type_for_description_in_key").value)
    similarity_type_for_description_in_value = float(Parameters.objects
                                                     .get(name="similarity_type_for_description_in_value").value)
    similarity_type_for_synonyms_in_value = float(Parameters.objects
                                                  .get(name="similarity_type_for_synonyms_in_value").value)
    similarity_type_for_synonyms_in_key = float(Parameters.objects
                                                .get(name="similarity_type_for_synonyms_in_key").value)

    tag_list = remove_tag_name(tag_list)
    for tag in tag_list:
        """
        If we found match with the description and the value of one tag OSM
        """
        if feature_code.name == tag.value:
            similarity_type_level = similarity_type_for_description_in_key
            return tag, similarity_type_level

        """
        If we found match with the description and the key of one tag OSM
        """
        if feature_code.name == tag.key and similarity_type_level < max(similarity_type_for_description_in_value,
                                                                        similarity_type_level):
            (tag_match, similarity_type_level) = (tag, max(similarity_type_for_description_in_value,
                                                           similarity_type_level))

        """
        If we found match with the description synonym and the value of one tag OSM
        """
        if tag.value in synonyms and similarity_type_level < max(similarity_type_for_synonyms_in_value,
                                                                 similarity_type_level):
            (tag_match, similarity_type_level) = (tag, max(similarity_type_for_synonyms_in_value,
                                                           similarity_type_level))

        """
        If we found match with the description synonym and the key of one tag OSM
        """
        if tag.key in synonyms and similarity_type_level < max(similarity_type_for_synonyms_in_key,
                                                               similarity_type_level):
            (tag_match, similarity_type_level) = (tag, max(similarity_type_for_synonyms_in_key, similarity_type_level))

    return tag_match, similarity_type_level
