#!/usr/bin/env python3

from django.core.management.base import BaseCommand, CommandError
from services.models import Relation, Tag, Node, Way, ScheduledWork, \
    SCHEDULED_WORK_IMPORTATION_PROCESS, PENDING, ERROR, FINALIZED, INPROGRESS, TagForClean
from datetime import datetime
from django.utils import timezone
from django.db import connection, transaction


class Command(BaseCommand):
    help = 'Clean the DB, suprime all the entities without name. '

    def add_arguments(self, parser):

        parser.add_argument(
            '--skip-clean-osm',
            action='store_true',
            dest='skip-clean-osm',
            default=False,
            help="Skip the clean of entities in osm"
        )

    def handle(self, *args, **options):
        """

        :param file: 
        :param args: 
        :param options: 
        :return: 
        """
        scheduled_work = ScheduledWork.objects.get(name=SCHEDULED_WORK_IMPORTATION_PROCESS, status=PENDING)

        scheduled_work.status = INPROGRESS
        scheduled_work.initial_date = timezone.now()
        scheduled_work.save()
        begin_process = datetime.now()

        try:
            if not options['skip-clean-osm']:
                self.stdout.write(
                    self.style.MIGRATE_LABEL("Cleaning OSM entities"))

                clean_entities_without_name(self)

            total_time = datetime.now() - begin_process

            scheduled_work.status = FINALIZED
            scheduled_work.final_date = timezone.now()
            scheduled_work.save()

            self.stdout.write(self.style.SUCCESS('Successfully importation process ", '
                                                 'time the execution de %s' % total_time))

        except Exception as detail:
            scheduled_work.status = ERROR
            scheduled_work.final_date = timezone.now()
            scheduled_work.save()

            raise CommandError(detail)


def generate_tag_for_clean(cursor):
    """
    This method generate a table with all the tags without name
    :param cursor: 
    :return: 
    """
    cursor.execute("TRUNCATE TABLE {0}".format(TagForClean._meta.db_table))

    cursor.execute("INSERT services_tagforclean SELECT t.id, t.reference FROM services_tag t " +
                   "WHERE NOT EXISTS (SELECT t2.id FROM services_tag t2 WHERE t2.reference = t.reference " +
                   "AND t2.key IN ('name', 'name:en'))")


def clean_entities_without_name(self):
    """
    This method take all the tags without name and suppress every entity with this tags.
    :param self: 
    :return: 
    """

    self.stdout.write(
        self.style.MIGRATE_HEADING("%s INFO: Cleaning OSM Entities" % datetime.now()))

    count = 0
    cursor = connection.cursor()
    generate_tag_for_clean(cursor)

    print("%s INFO: All tags loaded." % datetime.now())

    cursor.execute("SELECT t.id, t.reference FROM services_tagforclean t")
    all_tags = cursor.fetchall()

    print("%s INFO: All tags loaded." % datetime.now())
    transaction.set_autocommit(False)

    for tag_id, tag_reference in all_tags:
        count += 1
        try:
            Node.objects.filter(pk=tag_reference, relation_reference__isnull=True, way_reference__isnull=True).delete()
        except Exception:
            pass

        try:
            way = Way.objects.filter(pk=tag_reference, relation_reference__isnull=True).values()
            if way.id:
                Node.objects.filter(way_reference__id=way.id).delete()
                Way.objects.filter(pk=tag_reference, relation_reference__isnull=True).delete()
        except Way.DoesNotExist:
            pass

        try:
            relation = Relation.objects.get(pk=tag_reference, relation_reference__isnull=True)
            if relation.id:
                Node.objects.filter(relation_reference__id=relation.id).delete()
                Way.objects.filter(relation_reference__id=relation.id).delete()
                Relation.objects.filter(relation_reference__id=relation.id).delete()
                Relation.objects.filter(pk=relation.id)
        except Relation.DoesNotExist:
            pass

        Tag.objects.filter(pk=tag_id).delete()
        transaction.commit()

    transaction.set_autocommit(True)
    print("%s INFO: %d tags deleted." % (datetime.now(), count))

    self.stdout.write("Process ended ... " + self.style.SUCCESS("OK"))


def another_language(key):
    """
    This method verify if the tag has a name or not

    :param key:
    :return: 
    """
    try:
        if key[:5] == 'name:' and key != 'name:en':
            return True

    except IndexError:
        return False

    return False
