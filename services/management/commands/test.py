# !/usr/bin/env python3
from django.core.management.base import BaseCommand, CommandError
from services.classes.classes import PositionGPS
from util.coordinates_matching import matching_coordinates
from services.models import Geonames, Tag, ParametersScorePertinence
from services.classes.classes import EntityGeoNames
from services.algorithms.algorithm_align import match_type_correspondence, match_type_synonyms
from services.algorithms.algorithm_blocking import blocking_function
from decimal import *
from util.util import print_tags
from jellyfish import levenshtein_distance
from sklearn.model_selection import cross_val_score
from sklearn import tree
import numpy as np
from itertools import groupby, count

__author__ = 'Amaia Nazabal'


class Command(BaseCommand):
    help = 'This service allows import all the correspondences between types with a criteria related to the quantity' \
           ' of people how made the correspondences.'

    def handle(self, *args, **options):
        print("hello world")
        # array = generate_numpy_array_with_trainning_set()
        # print(array.data)
        # print(array)
        # print(array.dtype)
        #
        # print("features")
        # print(array[:, :1])
        #
        # print("target")
        # print(array[:, 3])
        #
        # sim_name_three = tree.DecisionTreeClassifier(random_state=0)
        # sim_name_three = sim_name_three.fit(array[:, :1], array[:, 3])
        #
        # float_values = np.arange(0, 1.1, 0.1)
        # print("float_values", float_values)
        # range_name = []
        # for i in float_values:
        #     another = i
        #     t = sim_name_three.predict([[i]])[0]
        #
        #     if t == float(1):
        #         range_name.append(float(str(another)))
        #
        #     print("For similarity name {0} classification gives {1}".format(i, t))
        #
        # ranges_name = runs(range_name)
        # print("ranges_name", ranges_name)
        #
        # max = 0
        # range_name = []
        # for range in ranges_name:
        #     if len(range) >= max:
        #         range_name = range
        #
        # print("Range name:", range_name[0], "-", range[-1])
        #



        # sim_type_three = tree.DecisionTreeClassifier()
        # sim_type_three = sim_type_three.fit(array[:, :1], array[:, 3])
        #
        # range_type = []
        # for i in float_values:
        #     t = sim_type_three.predict([[i]])[0]
        #
        #     if t == float(1):
        #         range_type.append(i)
        #
        #     print("For similarity type {0} classification gives {1}".format(i, t))
        #
        # sim_coordinates_three = tree.DecisionTreeClassifier()
        # sim_coordinates_three = sim_coordinates_three.fit(array[:, :1], array[:, 3])
        #
        # range_coordinates = []
        # for i in float_values:
        #     t = sim_coordinates_three.predict([[i]])[0]
        #
        #     if t == float(1):
        #         range_coordinates.append(i)
        #
        #     print("For similarity type {0} classification gives {1}".format(i, t))
        #


        # name = threshold_calculation_similarity_name()
        # coordinates = threshold_calculation_similarity_coordinates()
        # type = threshold_calculation_similarity_type()
        #
        # print(name, coordinates, type)
        #
        # total = name + coordinates + type
        # name = name / total
        # coordinates = coordinates / total
        # type = type / total
        #
        # print(name, coordinates, type)

        # try:

            # position_gn = PositionGPS(Decimal(42.5116200), Decimal(1.5340800))
            # position_osm = PositionGPS(Decimal(42.5114983), Decimal(1.5344814))
            #
            # coordinates_matching = matching_coordinates(position_gn, position_osm)
            # print(coordinates_matching)

            # gn_entity = Geonames.objects.get(pk=3017833)
            # geoname = EntityGeoNames(id=gn_entity.id, name=gn_entity.name, latitude=gn_entity.latitude,
            #                         longitude=gn_entity.longitude, feature_class=gn_entity.fclass,
            #                         feature_code=gn_entity.fcode)
            # list_block_entities = blocking_function(geoname)
            # print("BLOCKING LIST")
            # print(list_block_entities)
            #
            # position_gn = PositionGPS(gn_entity.latitude, gn_entity.longitude)
            #
            # for entity_osm in list_block_entities:
            #     print("------------------------------------------------------------")
                # tag_osm = type_tag_osm, matching_type_level = match_type_correspondence(geoname, entity_osm.get('tag_list'))
                # if not matching_type_level:
                #     tag_osm, _ = type_tag_osm, matching_type_level = match_type_synonyms(geoname, entity_osm.get('tag_list'))

                # print(geoname.get_feature_class(), geoname.get_feature_code())
                # print("TAG::::", tag_osm.key, tag_osm.value)
                # print("matching_type_level", matching_type_level)
                # print(entity_osm['entity_osm'])
                # print("------------------------------------------------------------")
                #
                # (latitude_osm, longitude_osm) = entity_osm['coordinates']
                # position_osm = PositionGPS(latitude_osm, longitude_osm)
                # coordinates_matching = matching_coordinates(position_gn, position_osm)


            # printtags = Tag.objects.distinct().only('key').all()
            # for tag in tags:
            #     key = tag.key
            #     try:
            #         if (key[:5] == 'name:' and key != 'name:en'):
            #             print("rejete ", key)
            #
            #     except IndexError:
            #         print("error ", key)

            # osm_type_key = None
            # osm_type_value = None
            # gn_feature_class = None
            # gn_feature_code = None
            # all_types = True
            #
            # params = ParametersScorePertinence.objects.filter(name='weight_matching',
            #                                                   osm_key_type=osm_type_key,
            #                                                   osm_value_type=osm_type_value,
            #                                                   gn_feature_class=gn_feature_class,
            #                                                   gn_feature_code=gn_feature_code,
            #                                                   all_types=all_types).values()[0]
            #
            # weight_geographical_coordinates = float(params['weight_coordinates'])
            # weight_name_matching = float(params['weight_name'])
            # weight_type_matching = float(params['weight_type'])
            #
            # print(weight_geographical_coordinates, weight_name_matching, weight_type_matching)

            # string1 = "Sercotel Andorra Park Hotel"
            # string2 = "Andorra Park"
            # print(levenshtein_distance(string1, string2))

        # except Exception as error:
        #     raise CommandError(error)
