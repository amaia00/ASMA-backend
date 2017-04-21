from django.db import models
from django.utils import timezone

__author__ = 'Amaia Nazábal'

NODE = 'NODE'
WAY = 'WAY'
AREA = 'AREA'
RELATION = 'RELATION'

STRUCTURE_TYPE = (
    (NODE, 'NODE'),
    (WAY, 'WAY'),
    (AREA, 'AREA'),
    (RELATION, 'RELATION')
)


class Tag(models.Model):
    id = models.AutoField(primary_key=True)

    reference = models.BigIntegerField()
    type = models.CharField(choices=STRUCTURE_TYPE, max_length=10, default='')

    key = models.CharField(max_length=100)
    value = models.CharField(max_length=300)


class Node(models.Model):
    id = models.BigIntegerField(unique=True, primary_key=True)

    # altitude and latitude precision
    # http://wiki.openstreetmap.org/wiki/Node#Structure
    latitude = models.DecimalField(decimal_places=7, max_digits=10)
    longitude = models.DecimalField(decimal_places=7, max_digits=11)

    way_reference = models.ForeignKey('Way', on_delete=models.CASCADE,
                                      null=True, blank=True)
    relation_reference = models.ForeignKey('Relation', on_delete=models.CASCADE,
                                           null=True, blank=True)
    role = models.CharField(max_length=50, null=True)
    correspondence_check = models.BooleanField(default=False)

    class Meta:
        index_together = ['latitude', 'longitude']


class Way(models.Model):

    id = models.IntegerField(unique=True, primary_key=True)

    relation_reference = models.ForeignKey('Relation', on_delete=models.CASCADE,
                                           null=True, blank=True)

    role = models.CharField(max_length=50, null=True)
    correspondence_check = models.BooleanField(default=False)


class Relation(models.Model):
    id = models.IntegerField(unique=True, primary_key=True)
    role = models.CharField(max_length=20, null=True)
    relation_reference = models.ForeignKey('Relation', on_delete=models.CASCADE,
                                           null=True, blank=True)
    correspondence_check = models.BooleanField(default=False)


class Geoname(models.Model):
    id = models.BigIntegerField(primary_key=True)
    name = models.CharField(max_length=200)
    ascii_name = models.CharField(max_length=200)
    alternative_name = models.CharField(max_length=10000)
    latitude = models.DecimalField(decimal_places=7, max_digits=11)
    longitude = models.DecimalField(decimal_places=7, max_digits=11)
    fclass = models.CharField(max_length=1)
    fcode = models.CharField(max_length=10)
    cc2 = models.CharField(max_length=200)
    admin1 = models.CharField(max_length=20)
    admin2 = models.CharField(max_length=80)
    admin3 = models.CharField(max_length=20)
    admin4 = models.CharField(max_length=20)
    population = models.BigIntegerField()
    elevation = models.IntegerField()
    gtopo30 = models.IntegerField()
    timezone = models.CharField(max_length=40)
    moddate = models.DateField()
    correspondence_check = models.BooleanField(default=False)

    class Meta:
        index_together = ['latitude', 'longitude']


# TODO make code column primary key and erase the unique index
class FeatureCode(models.Model):
    code = models.CharField(max_length=7, primary_key=True)
    name = models.CharField(max_length=200, blank=True)
    description = models.TextField()


class CorrespondenceEntity(models.Model):
    id = models.AutoField(primary_key=True)
    reference_gn = models.BigIntegerField()
    reference_osm = models.BigIntegerField()

    # geonames attributes
    gn_name = models.CharField(max_length=200, default='')
    gn_feature_class = models.CharField(max_length=1, default='')
    gn_feature_code = models.CharField(max_length=10, default='')
    gn_feature_name = models.CharField(max_length=200, default='')
    gn_latitude = models.DecimalField(decimal_places=7, max_digits=11, default=0)
    gn_longitude = models.DecimalField(decimal_places=7, max_digits=11, default=0)
    gn_type = models.CharField(choices=STRUCTURE_TYPE, default='NODE', max_length=10)

    # osm attributes
    osm_name = models.CharField(max_length=300, default='')
    osm_shape = models.CharField(choices=STRUCTURE_TYPE, default='', max_length=10)
    osm_key_type = models.CharField(max_length=50, default='')
    osm_value_type = models.CharField(max_length=300, default='')
    osm_latitude = models.DecimalField(decimal_places=7, max_digits=11, default=0)
    osm_longitude = models.DecimalField(decimal_places=7, max_digits=11, default=0)

    name_matching = models.DecimalField(decimal_places=3, max_digits=4, default=0)
    type_matching = models.DecimalField(decimal_places=3, max_digits=4, default=0)
    coordinates_matching = models.DecimalField(decimal_places=3, max_digits=4, default=0)

    pertinence_score = models.DecimalField(decimal_places=3, max_digits=4, default=0, null=True)
    date_matching = models.DateTimeField(auto_now_add=True, blank=True)

    class Meta:
        unique_together = ('reference_gn', 'reference_osm')


class CorrespondenceValide(models.Model):
    id = models.AutoField(primary_key=True)
    reference_gn = models.BigIntegerField()
    reference_osm = models.BigIntegerField()

    # geonames attributes
    gn_name = models.CharField(max_length=200, default='')
    gn_feature_class = models.CharField(max_length=1, default='')
    gn_feature_code = models.CharField(max_length=10, default='')
    gn_feature_name = models.CharField(max_length=200, default='')
    gn_latitude = models.DecimalField(decimal_places=7, max_digits=11, default=0)
    gn_longitude = models.DecimalField(decimal_places=7, max_digits=11, default=0)
    gn_type = models.CharField(choices=STRUCTURE_TYPE, default='NODE', max_length=10)

    # osm attributes
    osm_name = models.CharField(max_length=300, default='')
    osm_shape = models.CharField(choices=STRUCTURE_TYPE, default='', max_length=10)

    osm_latitude = models.DecimalField(decimal_places=7, max_digits=11, default=0)
    osm_longitude = models.DecimalField(decimal_places=7, max_digits=11, default=0)

    name_matching = models.DecimalField(decimal_places=3, max_digits=4, default=0)
    type_matching = models.DecimalField(decimal_places=3, max_digits=4, default=0)
    coordinates_matching = models.DecimalField(decimal_places=3, max_digits=4, default=0)

    pertinence_score = models.DecimalField(decimal_places=3, max_digits=4, default=0, null=True)
    date_validation = models.DateTimeField(auto_now_add=True, blank=True)

    class Meta:
        unique_together = ('reference_gn', 'reference_osm')


class CorrespondenceInvalide(models.Model):
    id = models.AutoField(primary_key=True)
    reference_gn = models.BigIntegerField()
    reference_osm = models.BigIntegerField()

    # geonames attributes
    gn_name = models.CharField(max_length=200, default='')
    gn_feature_class = models.CharField(max_length=1, default='')
    gn_feature_code = models.CharField(max_length=10, default='')
    gn_feature_name = models.CharField(max_length=200, default='')
    gn_latitude = models.DecimalField(decimal_places=7, max_digits=11, default=0)
    gn_longitude = models.DecimalField(decimal_places=7, max_digits=11, default=0)
    gn_type = models.CharField(choices=STRUCTURE_TYPE, default='NODE', max_length=10)

    # osm attributes
    osm_name = models.CharField(max_length=300, default='')
    osm_shape = models.CharField(choices=STRUCTURE_TYPE, default='', max_length=10)
    osm_key_type = models.CharField(max_length=50, default='')
    osm_value_type = models.CharField(max_length=300, default='')
    osm_latitude = models.DecimalField(decimal_places=7, max_digits=11, default=0)
    osm_longitude = models.DecimalField(decimal_places=7, max_digits=11, default=0)

    name_matching = models.DecimalField(decimal_places=3, max_digits=4, default=0)
    type_matching = models.DecimalField(decimal_places=3, max_digits=4, default=0)
    coordinates_matching = models.DecimalField(decimal_places=3, max_digits=4, default=0)

    pertinence_score = models.DecimalField(decimal_places=3, max_digits=4, default=0, null=True)
    date_invalidation = models.DateTimeField(auto_now_add=True, blank=True)

    class Meta:
        unique_together = ('reference_gn', 'reference_osm')


class ParametersScorePertinence(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    value = models.CharField(max_length=200)
    active = models.BooleanField(default=True)
    description = models.CharField(max_length=200)

    osm_key_type = models.CharField(max_length=50, default='', null=True)
    osm_value_type = models.CharField(max_length=300, default='', null=True)
    gn_feature_class = models.CharField(max_length=1, default='', null=True)
    gn_feature_code = models.CharField(max_length=10, default='', null=True)

    all_types = models.BooleanField(default=True, null=False)

    class Meta:
        unique_together = ('name', 'osm_key_type', 'osm_value_type', 'gn_feature_class', 'gn_feature_code', 'all_types')


class Parameters(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    value = models.CharField(max_length=200)
    active = models.BooleanField(default=True)
    description = models.CharField(max_length=200)


class CorrespondenceTypes(models.Model):
    id = models.AutoField(primary_key=True)
    gn_feature_class = models.CharField(max_length=1)
    gn_feature_code = models.CharField(max_length=10)

    osm_key = models.CharField(max_length=50)
    osm_value = models.CharField(max_length=300)

    description = models.CharField(max_length=500, null=True)

    class Meta:
        unique_together = ('gn_feature_class', 'gn_feature_code', 'osm_key', 'osm_value')


class CorrespondenceTypesClose(models.Model):
    id = models.AutoField(primary_key=True)
    gn_feature_class = models.CharField(max_length=1)
    gn_feature_code = models.CharField(max_length=10)

    osm_key = models.CharField(max_length=50)
    osm_value = models.CharField(max_length=300)
    date_validation = models.DateTimeField(blank=False, default=timezone.now)

