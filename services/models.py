from django.db import models
from django.utils import timezone

__author__ = 'Amaia Nazabal'

GEONAMES = 'GEONAMES'
OSM = 'OSM'

PROVIDERS = (
    (GEONAMES, GEONAMES),
    (OSM, OSM)
)

NODE = 'NODE'
WAY = 'WAY'
AREA = 'AREA'
RELATION = 'RELATION'

STRUCTURE_TYPE = (
    (NODE, NODE),
    (WAY, WAY),
    (AREA, AREA),
    (RELATION, RELATION)
)

PENDING = 'PENDING'
INPROGRESS = 'IN PROGRESS'
ERROR = 'ERROR'
FINALIZED = 'FINALIZED'

STRUCTURE_STATES = (
    (PENDING, PENDING),
    (INPROGRESS, INPROGRESS),
    (ERROR, ERROR),
    (FINALIZED, FINALIZED)
)

CALCULE = 0
VALIDE = 1
INVALIDE = 2

STRUCTURE_CORRESPONDENCES = (
    (CALCULE, CALCULE),
    (VALIDE, VALIDE),
    (INVALIDE, INVALIDE)
)

SCHEDULED_WORK_IMPORTATION_PROCESS = 'importation'
SCHEDULED_WORK_CORRESPONDENCE_PROCESS = 'global-match'
SCHEDULED_WORK_CORRESPONDENCE_TYPE = 'types-matching'
SCHEDULED_WORK_LEARNING_ALGORITHM = 'learning-algorithm'


class Tag(models.Model):
    id = models.AutoField(primary_key=True)

    reference = models.BigIntegerField()
    type = models.CharField(choices=STRUCTURE_TYPE, max_length=10, default='')

    key = models.CharField(max_length=100)
    value = models.CharField(max_length=300)


class TagForClean(models.Model):
    id = models.IntegerField(primary_key=True)
    reference = models.BigIntegerField(db_index=True)


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
    # Si le tag name de l'entite a été déjà cherché ou pas.
    checked_name = models.BooleanField(default=False)

    class Meta:
        index_together = ['latitude', 'longitude']


class Way(models.Model):

    id = models.IntegerField(unique=True, primary_key=True)

    relation_reference = models.ForeignKey('Relation', on_delete=models.CASCADE,
                                           null=True, blank=True)

    role = models.CharField(max_length=50, null=True)
    checked_name = models.BooleanField(default=False)


class Relation(models.Model):
    id = models.IntegerField(unique=True, primary_key=True)
    role = models.CharField(max_length=20, null=True)
    relation_reference = models.ForeignKey('Relation', on_delete=models.CASCADE,
                                           null=True, blank=True)
    checked_name = models.BooleanField(default=False)


class Geonames(models.Model):
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
    osm_key_type = models.CharField(max_length=50, blank=True)
    osm_value_type = models.CharField(max_length=300, blank=True)
    osm_latitude = models.DecimalField(decimal_places=7, max_digits=11, default=0)
    osm_longitude = models.DecimalField(decimal_places=7, max_digits=11, default=0)

    similarity_name = models.DecimalField(decimal_places=3, max_digits=4, default=0)
    similarity_type = models.DecimalField(decimal_places=3, max_digits=4, default=0)
    similarity_coordinates = models.DecimalField(decimal_places=3, max_digits=4, default=0)

    pertinence_score = models.DecimalField(decimal_places=3, max_digits=4, default=0, null=True)
    date_matching = models.DateTimeField(auto_now_add=True, blank=True)
    validation = models.IntegerField(choices=STRUCTURE_CORRESPONDENCES, default=CALCULE)
    weight_params = models.ForeignKey('ParametersScorePertinence', on_delete=models.CASCADE, blank=True, null=True)

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
    osm_key_type = models.CharField(max_length=50, blank=True)
    osm_value_type = models.CharField(max_length=300, blank=True)
    osm_latitude = models.DecimalField(decimal_places=7, max_digits=11, default=0)
    osm_longitude = models.DecimalField(decimal_places=7, max_digits=11, default=0)

    similarity_name = models.DecimalField(decimal_places=3, max_digits=4, default=0)
    similarity_type = models.DecimalField(decimal_places=3, max_digits=4, default=0)
    similarity_coordinates = models.DecimalField(decimal_places=3, max_digits=4, default=0)

    pertinence_score = models.DecimalField(decimal_places=3, max_digits=4, default=0, null=True)
    date_invalidation = models.DateTimeField(default=timezone.now)
    weight_params = models.ForeignKey('ParametersScorePertinence', on_delete=models.CASCADE, blank=True, null=True)

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
    osm_key_type = models.CharField(max_length=50, blank=True)
    osm_value_type = models.CharField(max_length=300, blank=True)
    osm_latitude = models.DecimalField(decimal_places=7, max_digits=11, default=0)
    osm_longitude = models.DecimalField(decimal_places=7, max_digits=11, default=0)

    similarity_name = models.DecimalField(decimal_places=3, max_digits=4, default=0)
    similarity_type = models.DecimalField(decimal_places=3, max_digits=4, default=0)
    similarity_coordinates = models.DecimalField(decimal_places=3, max_digits=4, default=0)

    pertinence_score = models.DecimalField(decimal_places=3, max_digits=4, default=0, null=True)
    date_invalidation = models.DateTimeField(default=timezone.now)
    weight_params = models.ForeignKey('ParametersScorePertinence', on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        unique_together = ('reference_gn', 'reference_osm')


class ParametersScorePertinence(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    active = models.BooleanField(default=True)

    weight_type = models.DecimalField(decimal_places=3, max_digits=4, default=0)
    weight_name = models.DecimalField(decimal_places=3, max_digits=4, default=0)
    weight_coordinates = models.DecimalField(decimal_places=3, max_digits=4, default=0)

    gn_feature_class = models.CharField(max_length=1, default='', null=True)
    gn_feature_code = models.CharField(max_length=10, default='', null=True)
    date = models.DateTimeField(default=timezone.now, blank=False)

    all_types = models.BooleanField(default=True, null=False)


class Parameters(models.Model):
    name = models.CharField(primary_key=True, max_length=50)
    value = models.CharField(max_length=300)
    active = models.BooleanField(default=True)
    description = models.CharField(max_length=200)
    client_name = models.CharField(max_length=60, default='')


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


class CorrespondenceTypesInvalid(models.Model):
    id = models.AutoField(primary_key=True)
    gn_feature_class = models.CharField(max_length=1)
    gn_feature_code = models.CharField(max_length=10)

    osm_key = models.CharField(max_length=50)
    osm_value = models.CharField(max_length=300)
    date_validation = models.DateTimeField(blank=False, default=timezone.now)
    quantity = models.IntegerField(default=0)
    active = models.BooleanField(default=False)

    class Meta:
        unique_together = ('gn_feature_class', 'gn_feature_code', 'osm_key', 'osm_value')


class ScheduledWork(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    total_rows = models.IntegerField(default=0)
    affected_rows = models.IntegerField(default=0)
    error_rows = models.IntegerField(default=0)
    file_name = models.CharField(max_length=100, default='')
    provider = models.CharField(choices=PROVIDERS, default='', max_length=10)
    status = models.CharField(choices=STRUCTURE_STATES, max_length=15, default=PENDING)
    initial_date = models.DateTimeField(blank=True, default=timezone.now)
    final_date = models.DateTimeField(null=True)
    process_id = models.IntegerField(default=0)


class CountryImported(models.Model):
    country_name = models.CharField(primary_key=True, max_length=100)
    date = models.DateTimeField(blank=True, default=timezone.now)


