#!/usr/bin/env python3

from django.core.management.base import BaseCommand, CommandError
from services.models import Relation, Tag, Node, Way, Geoname, FeatureCode, RELATION, NODE, WAY
import xml.etree.ElementTree as ET
from util.util import get_name_shape
from datetime import datetime


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def add_arguments(self, parser):

        parser.add_argument(
            'file',
            nargs='+',
            metavar="FILE",
            default=False,
            help="The path of the XML file for the OSM importation"
        )

        parser.add_argument(
            '--file2',
            default=False,
            metavar="FILE",
            help="The path of the dump for the geonames importation")

        parser.add_argument(
            '--file3',
            default=False,
            metavar="FILE",
            help="The path of the dump for the geonames feautures")

        parser.add_argument(
            '--skip-osm',
            action='store_true',
            dest='skip-osm',
            default=False,
            help='Skip the importation of the OSM dump',
        )

        parser.add_argument(
            '--skip-geonames',
            action='store_true',
            dest='skip-geonames',
            default=False,
            help='Skip the importation of the Geonames dump',
        )

        parser.add_argument(
            '--skip-features-geonames',
            action='store_true',
            dest='skip-features',
            default=False,
            help="Skip the features of geonames dump"
        )

        parser.add_argument(
            '--skip-clean-osm',
            action='store_true',
            dest='skip-clean-osm',
            default=False,
            help="Skip the clean of entities in osm"
        )

    def handle(self, file, *args, **options):
        """

        :param file: 
        :param args: 
        :param options: 
        :return: 
        """
        try:
            if not options['skip-osm']:
                for file in file:
                    begin_process = datetime.now()
                    self.stdout.write(
                        self.style.MIGRATE_LABEL("OSM Importation"))

                    tree = ET.parse(file)
                    print("%s INFO: File %s loaded." % (datetime.now(), file))

                    root = tree.getroot()
                    nodes_importation(self, root=root)
                    ways_importation(self, root=root)
                    relation_importation(self, root=root)

                    total_time = datetime.now() - begin_process

                    self.stdout.write(self.style.SUCCESS('Successfully importation process "%s", '
                                                         'time the execution de %s' % (file,
                                                                                       total_time)))

            if not options['skip-geonames']:
                self.stdout.write(
                    self.style.MIGRATE_LABEL("GeoNames Importation"))

                file = options['file2'] or file[0]
                geoname_importation(self, file)

                if not options['skip-features']:
                    file = options['file3']
                    features_importation(file)

            if not options['skip-clean-osm']:
                self.stdout.write(
                    self.style.MIGRATE_LABEL("Cleaning OSM entities"))

                clean_entities_without_name(self)

        except FileNotFoundError:
            raise CommandError('The file %s doesn\'t exists' % file)

        except IndexError as detail:
            print(detail)
            raise CommandError('Les fields n\'ont pas la meme structure.')
        except Exception as detail:
            raise CommandError(detail)


def geoname_importation(self, file):
    """
    This method execute the importation of geonames points.
    Read all the file and save every entity in the database
    
    :param file: 
    :return: 
    """

    print("%s INFO: Importation points geographiques." % datetime.now())

    #file_object = open(file, 'r')
    count = 0
    with open(file, encoding='utf-8') as file_object:
        for line in file_object:
            fields = line.split('\t')
            try:
                elevation = int(fields[15])
            except ValueError:
                elevation = 0

            try:
                geoname = Geoname(id=fields[0], name=fields[1], ascii_name=fields[2],
                                  alternative_name=fields[3].encode('utf-8'), latitude=fields[4],
                                  longitude=fields[5], fclass=fields[6], fcode=fields[7],
                                  cc2=fields[9], admin1=fields[10], admin2=fields[11],
                                  admin3=fields[12], admin4=fields[13], population=fields[14],
                                  elevation=elevation, gtopo30=fields[16], timezone=fields[17],
                                  moddate=fields[18])
                geoname.save()
                count += 1
            except Exception as error:
                print(line)
                self.stdout.write(
                    self.style.ERROR("One error in the importation" + str(error)))

    self.stdout.write(
        self.style.MIGRATE_HEADING("%s INFO: %d entities imported." % (datetime.now(), count)))
    file_object.close()


def features_importation(file):
    print("%s INFO: Importation feaures types." % datetime.now())

    file_object = open(file, 'r')
    count = 0

    for line in file_object:
        fields = line.split('\t')
        feature = FeatureCode(code=fields[0], name=fields[1], description=fields[2])
        feature.save()
        count += 1

    print("%s INFO: %d features imported." % (datetime.now(), count))
    file_object.close()


def nodes_importation(self, root):
    """
    Importation des noeuds OSM du fichier XML vers la BD relationnel avec ses tags
    :param root: le root du fichier XML pour parcourir l'arbre
    """
    count = 0
    for xml_point in root.iter('node'):
        point = Node(id=xml_point.get('id'), latitude=xml_point.get('lat'),
                     longitude=xml_point.get('lon'))
        point.save()
        count += 1

        for xml_tag in xml_point.findall('tag'):
            """
            On verifie que le tag soit ecrit en anglais et sinon, c'est pas necessaire
            de le garder dans la BD
            """
            if not another_language(xml_tag.get('k')):
                tag = Tag(reference=xml_point.get('id'), type=NODE,
                          key=xml_tag.get('k'), value=xml_tag.get('v'))
                tag.save()

        if len(xml_point.findall('tag')) > 0:
            print("%s INFO: %d tags imported." % (datetime.now(),
                                                  len(xml_point.findall('tag'))))

    self.stdout.write(
        self.style.MIGRATE_HEADING("%s INFO: %d nodes imported." % (datetime.now(), count)))


def ways_importation(self, root):
    """
    Importation des WAYs de OSM, avec ses tags et ses relations avec les noeuds
    :param root: le root du fichier XML pour parcourir l'arbre
    :return:
    """
    count = 0
    for xml_way in root.iter('way'):
        way = Way(id=xml_way.get('id'))
        way.save()
        count += 1

        for xml_sub_point in xml_way.findall('nd'):
            Node.objects.filter(pk=xml_sub_point.get('ref')) \
                .update(way_reference=xml_way.get('id'))

        for xml_tag in xml_way.findall('tag'):
            if not another_language(xml_tag.get('k')):
                tag = Tag(reference=xml_way.get('id'), type=WAY,
                          key=xml_tag.get('k'), value=xml_tag.get('v'))
                tag.save()

        if len(xml_way.findall('tag')) > 0:
            print("%s INFO: %d tags imported." % (datetime.now(),
                                                  len(xml_way.findall('tag'))))

        if len(xml_way.findall('nd')) > 0:
            print("%s INFO: %d noeuds imported." % (datetime.now(),
                                                    len(xml_way.findall('nd'))))

    self.stdout.write(
        self.style.MIGRATE_HEADING("%s INFO: %d ways imported." % (datetime.now(), count)))


def relation_importation(self, root):
    """
    Importation des relations OSM vers la BD relationnel, avec ses tags et membres.
    :param root:
    :return:
    """
    count = 0
    for xml_relation in root.iter('relation'):
        relation = Relation(id=xml_relation.get('id'), role=xml_relation.get('role') or '')
        relation.save()
        count += 1

        for xml_tag in xml_relation.findall('tag'):
            if not another_language(xml_tag.get('k')):
                tag = Tag(reference=xml_relation.get('id'), type=RELATION,
                          key=xml_tag.get('k'), value=xml_tag.get('v'))
                tag.save()

        print("%s INFO: %d tags imported." % (datetime.now(),
                                              len(xml_relation.findall('tag'))))

        for xml_member in xml_relation.findall('member'):
            if xml_member.get('type') == 'node':
                Node.objects.filter(pk=xml_member.get('ref')) \
                    .update(relation_reference=xml_relation.get('id'),
                            role=xml_member.get('role'))
            elif xml_member.get('type') == 'way':
                Way.objects.filter(pk=xml_member.get('ref')) \
                    .update(relation_reference=xml_relation.get('id'),
                            role=xml_member.get('role'))
            elif xml_member.get('type') == 'relation':
                Relation.objects.filter(pk=xml_member.get('ref')) \
                    .update(relation_reference=xml_relation.get('id'),
                            role=xml_member.get('role'))

        print("%s INFO: %d members imported." % (datetime.now(),
                                                 len(xml_relation.findall('member'))))

    self.stdout.write(
        self.style.MIGRATE_HEADING("%s INFO: %d relations imported." % (datetime.now(), count)))


def clean_entities_without_name(self):
    count = 0
    fathers_nodes = Node.objects.filter(relation_reference__isnull=True, way_reference__isnull=True, checked_name=False)
    for node in fathers_nodes:
        tag_list = Tag.objects.filter(reference=node.id)
        name, _ = get_name_shape(tag_list)
        if not name:
            node.delete()
            count += 1
    fathers_nodes.update(checked_name=True)

    print("%s INFO: %d nodes deleted." % (datetime.now(), count))

    count = 0
    count_nodes = 0
    fathers_ways = Way.objects.filter(relation_reference_id__isnull=True, checked_name=False)
    for way in fathers_ways:
        tag_list = Tag.objects.filter(reference=way.id)
        name, _ = get_name_shape(tag_list)
        if not name:
            way.delete()
            count_nodes += Node.objects.filter(way_reference=way.id).count()
            Node.objects.filter(way_reference=way.id).delete()

            count += 1

    fathers_ways.update(checked_name=True)
    print("%s INFO: %d ways deleted." % (datetime.now(), count))
    print("%s INFO: %d nodes linked to this ways deleted." % (datetime.now(), count_nodes))

    count = 0
    count_nodes = 0
    count_ways = 0

    fathers_relations = Relation.objects.filter(relation_reference__isnull=True, checked_name=False)
    for relation in fathers_relations:
        tag_list = Tag.objects.filter(reference=relation.id)
        name, _ = get_name_shape(tag_list)

        if not name:
            count_nodes += Node.objects.filter(relation_reference=relation.id).count()
            Node.objects.filter(relation_reference=relation.id).delete()

            ways = Way.objects.filter(relation_reference=relation.id)
            count_ways += ways.count()
            Way.objects.filter(relation_reference=relation.id).delete()

            for way in ways:
                count_nodes += Node.objects.filter(way_reference=way.id).count()
                Node.objects.filter(way_reference=way.id).delete()

            relation.delete()
            count += 1

    fathers_relations.update(checked_name=True)

    print("%s INFO: %d relation deleted." % (datetime.now(), count))
    print("%s INFO: %d ways linked to this relations deleted." % (datetime.now(), count_ways))
    print("%s INFO: %d nodes linked to this ways deleted." % (datetime.now(), count_nodes))

    self.stdout.write("Process ended ... " + self.style.SUCCESS("OK"))


def another_language(key):
    """

    :param key:
    :return: 
    """
    try:
        if key[:5] == 'name:' and key != 'name:en':
            return True

    except IndexError:
        return False

    return False
