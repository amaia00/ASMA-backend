from rest_framework import serializers
from .models import Node, Tag, Way, Relation, Parameters, CorrespondenceEntity, CorrespondenceValide, Geoname, \
    FeatureCode, CorrespondenceTypes, CorrespondenceTypesClose, CorrespondenceInvalide


class TagSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'reference', 'type', 'key', 'value')


class PointSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Node
        fields = ('id', 'latitude', 'longitude', 'way_reference', 'relation_reference')


class WaySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Way
        fields = ('id', 'relation_reference')


class RelationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Relation
        fields = ('id', 'role')


class GeonameSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Geoname
        fields = ('id', 'name', 'ascii_name', 'alternative_name', 'latitude', 'longitude',
                  'fclass', 'fcode', 'cc2', 'admin1', 'admin2', 'admin3', 'admin4', 'population',
                  'elevation', 'gtopo30', 'timezone', 'moddate')


class FeatureCodeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = FeatureCode
        fields = ('id', 'code', 'name', 'description')


class CorrespondenceEntitySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CorrespondenceEntity
        fields = ('id', 'reference_gn', 'reference_osm',
                  'gn_feature_class', 'gn_feature_code', 'osm_key', 'osm_value',
                  'name_levenshtein', 'type_matching', 'pertinence_score')


class CorrespondenceValideSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CorrespondenceValide
        fields = ('id', 'reference_gn', 'reference_osm',
                  'gn_feature_class', 'gn_feature_code', 'osm_key', 'osm_value',
                  'name_levenshtein', 'type_matching', 'pertinence_score', 'date_validation')


class CorrespondenceInvalideSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CorrespondenceInvalide
        fields = ('id', 'reference_gn', 'reference_osm',
                  'gn_feature_class', 'gn_feature_code', 'osm_key', 'osm_value',
                  'name_levenshtein', 'type_matching', 'pertinence_score', 'date_validation')


class ParameterSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Parameters
        fields = ('id', 'name', 'value', 'description')


class CorrespondenceTypesSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CorrespondenceTypes
        fields = ('id', 'gn_feature_class', 'gn_feature_code', 'osm_key', 'osm_value', 'description')


class CorrespondenceTypesCloseSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CorrespondenceTypesClose
        fields = ('id', 'gn_feature_class', 'gn_feature_code', 'osm_key', 'osm_value', 'description')