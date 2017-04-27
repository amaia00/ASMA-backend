# !/usr/bin/env python3
from django.core.management.base import BaseCommand, CommandError
from services.models import CorrespondenceTypes, CorrespondenceTypesClose, SCHEDULED_WORK_CORRESPONDENCE_TYPE, \
    INPROGRESS, ScheduledWork, PENDING, ERROR
from django.db import connection
from datetime import datetime
from django.utils import timezone

__author__ = 'Amaia Nazabal'


class Command(BaseCommand):
    help = 'This service allows import all the correspondences between types with a criteria related to the quantity' \
           ' of people how made the correspondences.'

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.MIGRATE_LABEL('%s : The process begins.' %
                                     (datetime.now())))
        scheduled_work = ScheduledWork.objects.get(name=SCHEDULED_WORK_CORRESPONDENCE_TYPE, status=PENDING)

        try:
            scheduled_work.status = INPROGRESS
            scheduled_work.total_rows = 0
            scheduled_work.initial_date = timezone.now()
            scheduled_work.save()

            self.stdout.write(
                self.style.MIGRATE_HEADING('%s : Correspondences in the set of correspondences valides.' %
                                           (datetime.now())))

            cursor = connection.cursor()
            # types_matching_valide_quantity
            cursor.execute("SELECT v.gn_feature_class, v.gn_feature_code, v.osm_key_type, v.osm_value_type, COUNT(0)" +
                           " FROM services_correspondencevalide v WHERE NOT EXISTS(SELECT st.id FROM " +
                           "services_correspondencetypes st WHERE st.osm_key = v.osm_key_type AND st.osm_value = " +
                           "v.osm_value_type AND st.gn_feature_code = v.gn_feature_code AND st.gn_feature_class = " +
                           "v.gn_feature_class) GROUP BY v.gn_feature_class, v.gn_feature_code, v.osm_key_type, " +
                           "v.osm_value_type HAVING COUNT(0) > (SELECT p.value FROM services_parameters p WHERE " +
                           " p.name= 'types_matching_valide_quantity')")

            all = cursor.fetchall()
            scheduled_work.total_rows += len(all)
            scheduled_work.save()
            for feature_class, feature_code, osm_type_key, osm_type_value, _ in all:
                type_correspondence = CorrespondenceTypesClose(gn_feature_code=feature_code,
                                                               gn_feature_class=feature_class,
                                                               osm_key=osm_type_key, osm_value=osm_type_value)
                type_correspondence.save()
                scheduled_work.affected_rows += 1
                scheduled_work.save()

            self.stdout.write(
                '%s : The process ended with %s new correspondences in the valide set...' %
                (datetime.now(), str(len(all))) + self.style.SUCCESS("OK"))

            self.stdout.write(
                self.style.MIGRATE_HEADING('%s : Correspondences in the set of correspondences closes.' %
                                           (datetime.now())))

            cursor.execute("SELECT v.gn_feature_class, v.gn_feature_code, v.osm_key, v.osm_value, COUNT(0) " +
                           "FROM services_correspondencetypesclose v WHERE NOT EXISTS(SELECT st.id FROM " +
                           "services_correspondencetypes st WHERE st.osm_key = v.osm_key AND st.osm_value = " +
                           "v.osm_value AND st.gn_feature_code = v.gn_feature_code AND st.gn_feature_class = " +
                           "v.gn_feature_class) GROUP BY v.gn_feature_class, v.gn_feature_code, v.osm_key, " +
                           "v.osm_value HAVING COUNT(0) > (SELECT p.value FROM services_parameters p WHERE " +
                           "p.name= 'types_matching_close_quantity')")
            all = cursor.fetchall()

            scheduled_work.total_rows += len(all)
            scheduled_work.save()

            for feature_class, feature_code, osm_type_key, osm_type_value, _ in all:
                type_correspondence = CorrespondenceTypes(gn_feature_code=feature_code, gn_feature_class=feature_class,
                                                          osm_key=osm_type_key, osm_value=osm_type_value)
                type_correspondence.save()
                CorrespondenceTypesClose.objects.filter(gn_feature_code=feature_code, gn_feature_class=feature_class,
                                                        osm_key=osm_type_key, osm_value=osm_type_value).delete()
                scheduled_work.affected_rows += 1
                scheduled_work.save()

            self.stdout.write('%s : The process ended with %s new correspondences in the close set....' %
                              (datetime.now(), str(len(all))) + self.style.SUCCESS("OK"))

        except Exception as error:
            scheduled_work.status = ERROR
            scheduled_work.save()
            raise CommandError(error)
