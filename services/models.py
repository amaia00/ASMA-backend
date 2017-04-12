from django.db import models

__author__ = 'Amaia Nazábal'

NODE = 0
WAY = 1
RELATION = 2

STRUCTURE_TYPE = (
    (NODE, 'NODE'),
    (WAY, 'WAY'),
    (RELATION, 'RELATION')
)


class Tag(models.Model):
    id = models.AutoField(primary_key=True)

    reference = models.BigIntegerField()
    type = models.IntegerField(choices=STRUCTURE_TYPE)

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

    class Meta:
        index_together = ['latitude', 'longitude']


class Way(models.Model):

    id = models.IntegerField(unique=True, primary_key=True)

    relation_reference = models.ForeignKey('Relation', on_delete=models.CASCADE,
                                           null=True, blank=True)

    role = models.CharField(max_length=50, null=True)


class Relation(models.Model):
    id = models.IntegerField(unique=True, primary_key=True)
    role = models.CharField(max_length=20, null=True)
    relation_reference = models.ForeignKey('Relation', on_delete=models.CASCADE,
                                           null=True, blank=True)


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
    gn_feature_class = models.CharField(max_length=1, default='')
    gn_feature_code = models.CharField(max_length=10, default='')
    gn_latitude = models.DecimalField(decimal_places=7, max_digits=11, default=0)
    gn_longitude = models.DecimalField(decimal_places=7, max_digits=11, default=0)

    # osm attributes
    osm_name = models.CharField(max_length=300, default='')
    osm_key_type = models.CharField(max_length=50, default='')
    osm_value_type = models.CharField(max_length=300, default='')
    osm_latitude = models.DecimalField(decimal_places=7, max_digits=11, default=0)
    osm_longitude = models.DecimalField(decimal_places=7, max_digits=11, default=0)

    name_levenshtein = models.DecimalField(decimal_places=3, max_digits=4, default=0)
    type_matching = models.DecimalField(decimal_places=3, max_digits=4, default=0)

    pertinence_score = models.DecimalField(decimal_places=3, max_digits=4, default=0, null=True)

    class Meta:
        unique_together = ('reference_gn', 'reference_osm')


class CorrespondenceValide(models.Model):
    id = models.AutoField(primary_key=True)
    reference_gn = models.BigIntegerField()
    reference_osm = models.BigIntegerField()

    # geonames attributes
    gn_feature_class = models.CharField(max_length=1, default='')
    gn_feature_code = models.CharField(max_length=10, default='')
    gn_latitude = models.DecimalField(decimal_places=7, max_digits=11, default=0)
    gn_longitude = models.DecimalField(decimal_places=7, max_digits=11, default=0)

    # osm attributes
    osm_name = models.CharField(max_length=300, default='')
    osm_key_type = models.CharField(max_length=50, default='')
    osm_value_type = models.CharField(max_length=300, default='')
    osm_latitude = models.DecimalField(decimal_places=7, max_digits=11, default=0)
    osm_longitude = models.DecimalField(decimal_places=7, max_digits=11, default=0)

    name_levenshtein = models.DecimalField(decimal_places=3, max_digits=4, default=0)
    type_matching = models.DecimalField(decimal_places=3, max_digits=4, default=0)

    pertinence_score = models.DecimalField(decimal_places=3, max_digits=4, default=0, null=True)
    date_validation = models.DateTimeField(auto_now_add=True, blank=True)

    class Meta:
        unique_together = ('reference_gn', 'reference_osm')


class CorrespondenceInvalide(models.Model):
    id = models.AutoField(primary_key=True)
    reference_gn = models.BigIntegerField()
    reference_osm = models.BigIntegerField()

    # geonames attributes
    gn_feature_class = models.CharField(max_length=1, default='')
    gn_feature_code = models.CharField(max_length=10, default='')
    gn_latitude = models.DecimalField(decimal_places=7, max_digits=11, default=0)
    gn_longitude = models.DecimalField(decimal_places=7, max_digits=11, default=0)

    # osm attributes
    osm_name = models.CharField(max_length=300, default='')
    osm_key_type = models.CharField(max_length=50, default='')
    osm_value_type = models.CharField(max_length=300, default='')
    osm_latitude = models.DecimalField(decimal_places=7, max_digits=11, default=0)
    osm_longitude = models.DecimalField(decimal_places=7, max_digits=11, default=0)

    name_levenshtein = models.DecimalField(decimal_places=3, max_digits=4, default=0)
    type_matching = models.DecimalField(decimal_places=3, max_digits=4, default=0)

    pertinence_score = models.DecimalField(decimal_places=3, max_digits=4, default=0, null=True)
    date_validation = models.DateTimeField(auto_now_add=True, blank=True)

    class Meta:
        unique_together = ('reference_gn', 'reference_osm')


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
    description = models.CharField(max_length=500, null=True)

    class Meta:
        unique_together = ('gn_feature_class', 'gn_feature_code', 'osm_key', 'osm_value')
