#!/usr/bin/env python3

from django.core.management.base import BaseCommand, CommandError
from services.models import Relation, Tag, Node, Way, Geoname, FeatureCode, RELATION, NODE, WAY
import xml.etree.ElementTree as ET
from datetime import datetime


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def add_arguments(self, parser):

        parser.add_argument(
            'file',
            nargs='+',
            metavar="FILE",
            help="The path of the XML file for the OSM importation")

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

    def handle(self, file, *args, **options):
        """

        :param file:
        :param args:
        :param options:
        :return:
        """
        if not options['skip-osm']:
            for file in file:
                try:
                    begin_process = datetime.now()
                    print("===================================")
                    print("          OSM Importation          ")
                    print("===================================")

                    tree = ET.parse(file)
                    print("%s INFO: File %s loaded." % (datetime.now(), file))

                    root = tree.getroot()
                    nodes_importation(root=root)
                    ways_importation(root=root)
                    relation_importation(root=root)

                    total_time = datetime.now() - begin_process

                    self.stdout.write(self.style.SUCCESS('Successfully importation process "%s", '
                                                         'time the execution de %s' % (file,
                                                                                       total_time)))
                except OSError:
                    raise CommandError('The file %s doesn\'t exists.' % file)

        if not options['skip-geonames']:
            print("===================================")
            print("       GeoNames Importation        ")
            print("===================================")

            try:
                file = options['file2'] or file[0]
                geoname_importation(file)

                if not options['skip-features']:
                    file = options['file3']
                    features_importation(file)

            except FileNotFoundError:
                raise CommandError('The file %s doesn\'t exists' % file)
            except IndexError as detail:
                print(detail)
                raise CommandError('Les fields n\'ont pas la meme structure.')


def geoname_importation(file):

    #This method execute the importation of geonames points.
    #Read all the file and save every entity in the database
    #:param file:
    #:return:

    print("%s INFO: Importation points geographiques." % datetime.now())

    file_object = open(file, 'r')
    count = 0
    for line in file_object:
        fields = line.split('\t')
        try:
            elevation = int(fields[15])
        except ValueError:
            elevation = 0

        geoname = Geoname(id=fields[0], name=fields[1], ascii_name=fields[2],
                          alternative_name=fields[3], latitude=fields[4],
                          longitude=fields[5], fclass=fields[6], fcode=fields[7],
                          cc2=fields[9], admin1=fields[10], admin2=fields[11],
                          admin3=fields[12], admin4=fields[13], population=fields[14],
                          elevation=elevation, gtopo30=fields[16], timezone=fields[17],
                          moddate=fields[18])
        geoname.save()
        count += 1

    print("%s INFO: %d entitys imported." % (datetime.now(), count))
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


def nodes_importation(root):
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

    print("-----------------------------------")
    print("%s INFO: %d nodes imported." % (datetime.now(), count))
    print("-----------------------------------")


def ways_importation(root):
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

        for xml_tag in xml_way.findall('tag'):
            if not another_language(xml_tag.get('k')):
                tag = Tag(reference=xml_way.get('id'), type=WAY,
                          key=xml_tag.get('k'), value=xml_tag.get('v'))
                tag.save()

        if len(xml_way.findall('tag')) > 0:
            print("%s INFO: %d tags imported." % (datetime.now(),
                                                  len(xml_way.findall('tag'))))

        for xml_sub_point in xml_way.findall('nd'):
            Node.objects.filter(pk=xml_sub_point.get('ref')) \
                .update(way_reference=xml_way.get('id'))

        if len(xml_way.findall('nd')) > 0:
            print("%s INFO: %d noeuds imported." % (datetime.now(),
                                                    len(xml_way.findall('nd'))))

    print("-----------------------------------")
    print("%s INFO: %d ways imported." % (datetime.now(), count))
    print("-----------------------------------")


def relation_importation(root):
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
                            role=xml_relation.get('role'))
            elif xml_member.get('type') == 'way':
                Way.objects.filter(pk=xml_member.get('ref')) \
                    .update(relation_reference=xml_relation.get('id'),
                            role=xml_relation.get('role'))
            elif xml_member.get('type') == 'relation':
                Relation.objects.filter(pk=xml_member.get('ref')) \
                    .update(relation_reference=xml_relation.get('id'),
                            role=xml_relation.get('role'))

        print("%s INFO: %d members imported." % (datetime.now(),
                                                 len(xml_relation.findall('member'))))

    print("-----------------------------------")
    print("%s INFO: %d relations imported." % (datetime.now(), count))
    print("-----------------------------------")


def another_language(key):
    """

    :param key:
    :return:
    """
    try:
        if key[-3:][:1] != ':' or key[-3:] == ':en' and key[5] != 'name:' or key == 'name:en':
                return False

    except IndexError:
        return False

    return True
