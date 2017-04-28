from rest_framework import serializers
from .models import Node, Tag, Way, Relation, Parameters, CorrespondenceEntity, CorrespondenceValide, Geonames, \
    FeatureCode, CorrespondenceTypes, CorrespondenceTypesClose, CorrespondenceInvalide, ParametersScorePertinence, ScheduledWork, CountryImported


class TagSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'reference', 'type', 'key', 'value')


class PointSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Node
        fields = ('id', 'latitude', 'longitude', 'way_reference', 'relation_reference', 'checked_name')


class WaySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Way
        fields = ('id', 'relation_reference', 'role')


class RelationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Relation
        fields = ('id', 'role', 'relation_reference')


class GeonameSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Geonames
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
                  'gn_name', 'gn_feature_class', 'gn_feature_code', 'gn_feature_name', 'gn_latitude', 'gn_longitude',
                  'osm_name', 'osm_key_type', 'osm_value_type', 'osm_latitude', 'osm_longitude', 'osm_shape',
                  'similarity_name', 'similarity_type', 'similarity_coordinates', 'pertinence_score', 'validation')


class CorrespondenceValideSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CorrespondenceValide
        fields = ('id', 'reference_gn', 'reference_osm',
                  'gn_name', 'gn_feature_class', 'gn_feature_code', 'gn_feature_name', 'gn_latitude', 'gn_longitude',
                  'osm_name', 'osm_key_type', 'osm_value_type', 'osm_latitude', 'osm_longitude', 'osm_shape',
                  'similarity_name', 'similarity_type', 'similarity_coordinates', 'pertinence_score')


class CorrespondenceInvalideSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CorrespondenceInvalide
        fields = ('id', 'reference_gn', 'reference_osm',
                  'gn_name', 'gn_feature_class', 'gn_feature_code', 'gn_feature_name', 'gn_latitude', 'gn_longitude',
                  'osm_name', 'osm_key_type', 'osm_value_type', 'osm_latitude', 'osm_longitude', 'osm_shape',
                  'similarity_name', 'similarity_type', 'similarity_coordinates', 'pertinence_score')


class ParameterSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Parameters
        fields = ('name', 'value', 'description')


class ParametersScorePertinenceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ParametersScorePertinence
        fields = ('id', 'name', 'weight_type', 'weight_name', 'weight_coordinates',
                  'gn_feature_class', 'gn_feature_code', 'all_types', 'date')


class CorrespondenceTypesSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CorrespondenceTypes
        fields = ('id', 'gn_feature_class', 'gn_feature_code', 'osm_key', 'osm_value', 'description')


class CorrespondenceTypesCloseSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CorrespondenceTypesClose
        fields = ('id', 'gn_feature_class', 'gn_feature_code', 'osm_key', 'osm_value',)


class ScheduledWorkSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ScheduledWork
        fields = ('id', 'name', 'total_rows', 'affected_rows', 'error_rows', 'file_name', 'provider','status',
                  'initial_date', 'final_date', 'process_id')


class CountryImportedSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CountryImported
        fields = ('name', 'date')