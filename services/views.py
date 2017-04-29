from rest_framework import viewsets, permissions, views, status, parsers, mixins
from rest_framework.response import Response
from rest_framework.request import Request
from django.conf import settings
from .permissions import ReadOnlyPermission
from .models import Tag, Node, Way, Relation, Parameters, CorrespondenceValide, CorrespondenceEntity, Geonames, \
    FeatureCode, CorrespondenceTypes, CorrespondenceTypesClose, CorrespondenceInvalide, ParametersScorePertinence, \
    ScheduledWork, VALIDE, INVALIDE, SCHEDULED_WORK_IMPORTATION_PROCESS, CountryImported
from .serializer import TagSerializer, PointSerializer, WaySerializer, RelationSerializer, \
    CorrespondenceValideSerializer, CorrespondenceEntitySerializer, ParameterSerializer, GeonameSerializer, \
    FeatureCodeSerializer, CorrespondenceTypesSerializer, CorrespondenceTypesCloseSerializer, \
    CorrespondenceInvalideSerializer, ParametersScorePertinenceSerializer, ScheduledWorkSerializer, \
    CountryImportedSerializer
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.contrib.auth import authenticate, login
from rest_framework.renderers import JSONRenderer
from services.classes.thread import BackgroundProcess
import random


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (ReadOnlyPermission,)

    def get_queryset(self):
        queryset = Tag.objects.all()
        reference = self.request.query_params.get('reference', None)
        if reference is not None:
            queryset = queryset.filter(reference=reference).exclude(key__contains="name")

        return queryset


class PointViewSet(viewsets.ModelViewSet):
    queryset = Node.objects.all()
    serializer_class = PointSerializer
    permission_classes = (ReadOnlyPermission,)


class WayViewSet(viewsets.ModelViewSet):
    queryset = Way.objects.all()
    serializer_class = WaySerializer
    permission_classes = (ReadOnlyPermission,)


class RelationViewSet(viewsets.ModelViewSet):
    queryset = Relation.objects.all()
    serializer_class = RelationSerializer
    permission_classes = (ReadOnlyPermission,)


class GeonamesViewSet(viewsets.ModelViewSet):
    queryset = Geonames.objects.all()
    serializer_class = GeonameSerializer
    permission_classes = (ReadOnlyPermission,)


class FeatureCodeViewSet(viewsets.ModelViewSet):
    queryset = FeatureCode.objects.all()
    serializer_class = FeatureCodeSerializer
    permission_classes = (ReadOnlyPermission,)


class ParametersViewSet(viewsets.ModelViewSet):
    queryset = Parameters.objects.filter(active=1).all()
    serializer_class = ParameterSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


class ParametersScorePertinenceViewSet(viewsets.ModelViewSet):
    queryset = ParametersScorePertinence.objects.all()
    serializer_class = ParametersScorePertinenceSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        queryset = ParametersScorePertinence.objects.filter(active=1).all()
        return queryset

    def create(self, request, *args, **kwargs):
        if request.data['all_types'] == 1:
            ParametersScorePertinence.objects.filter(all_types=1).update(active=0)
        else:
            ParametersScorePertinence.objects.filter(gn_feature_class=request.data['gn_feature_class'],
                                                     gn_feature_code=request.data['gn_feature_code']).update(active=0)

        serializer = ParametersScorePertinenceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ParametersScorePertinenceHistoryViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin,
                                              viewsets.GenericViewSet):
    queryset = ParametersScorePertinence.objects.all()
    serializer_class = ParametersScorePertinenceSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        all_types = self.request.query_params.get('all_types', None)
        gn_feature_class = self.request.query_params.get('gn_feature_class', None)
        gn_feature_code = self.request.query_params.get('gn_feature_code', None)

        if all_types == 1:
            queryset = ParametersScorePertinence.objects.filter(active=0, all_types=all_types).all().order_by('-date')

        elif gn_feature_class is not None:
            queryset = ParametersScorePertinence.objects.filter(active=0, gn_feature_class=gn_feature_class,
                                                                gn_feature_code=gn_feature_code).all().order_by('-date')
        else:
            queryset = ParametersScorePertinence.objects.filter(active=0).order_by('-date')

        return queryset


class CorrespondenceEntityView(viewsets.ViewSet):
    def list(self, request, format=None):

        if request.GET.get('osm') and request.GET.get('gn'):
            try:
                correspondence = CorrespondenceEntity.objects.filter(reference_osm=int(request.GET.get('osm')),
                                                                     reference_gn=int(request.GET.get('gn'))).order_by(
                    '-pertinence_score')

                serializer = CorrespondenceEntitySerializer(correspondence, many=True)
                print("SERIALIZER DATA: ", correspondence)

            except CorrespondenceEntity.DoesNotExist:
                return Response(status=status.HTTP_400_BAD_REQUEST)

        elif request.GET.get('gn'):
            try:
                correspondence = CorrespondenceEntity.objects.filter(reference_gn=int(request.GET.get('gn'))).order_by(
                    '-pertinence_score')
                serializer = CorrespondenceEntitySerializer(correspondence, many=True)

            except CorrespondenceEntity.DoesNotExist:
                return Response(status=status.HTTP_400_BAD_REQUEST)

        elif request.GET.get('osm'):
            try:
                correspondence = CorrespondenceEntity.objects.filter(
                    reference_osm=int(request.GET.get('osm'))).order_by('-pertinence_score')

                serializer = CorrespondenceEntitySerializer(correspondence, many=True)

            except CorrespondenceEntity.DoesNotExist:
                return Response(status=status.HTTP_400_BAD_REQUEST)

        else:
            correspondences = CorrespondenceEntity.objects.filter(similarity_name__gt=0, similarity_coordinates__gt=0,
                                                                  similarity_type__gt=0).all()
            paginator = Paginator(correspondences, settings.REST_FRAMEWORK['PAGE_SIZE'])
            page = request.GET.get('page')

            try:
                correspondences_by_page = paginator.page(page)
            except PageNotAnInteger:
                # If page is not an integer, deliver first page.
                correspondences_by_page = paginator.page(1)
            except EmptyPage:
                # If page is out of range (e.g. 9999), deliver last page of results.
                correspondences_by_page = paginator.page(paginator.num_pages)

            serializer = CorrespondenceEntitySerializer(correspondences_by_page, many=True)

        return Response(serializer.data)


class CorrespondenceValideView(viewsets.ViewSet):
    def list(self, request, format=None):

        # http://127.0.0.1:8000/correspondence-valide/?osm=194554955&gn=822469
        if request.GET.get('osm') and request.GET.get('gn'):
            try:
                correspondence = CorrespondenceValide.objects.get(reference_osm=int(request.GET.get('osm')),
                                                                  reference_gn=int(request.GET.get('gn')))
            except CorrespondenceValide.DoesNotExist:
                return Response(status=status.HTTP_400_BAD_REQUEST)

            serializer = CorrespondenceValideSerializer(correspondence)

        else:
            # http://127.0.0.1:8000/correspondence-valide
            correspondences = CorrespondenceValide.objects.all()
            serializer = CorrespondenceValideSerializer(correspondences, many=True)

        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = CorrespondenceValideSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()

            CorrespondenceEntity.objects.filter(reference_gn=request.data['reference_gn'],
                                                reference_osm=request.data['reference_osm']).update(validation=VALIDE)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EntityOSMDetails(viewsets.ViewSet):
    def list(self, request, id, format=None):

        serializer_context = {
            'request': Request(request),
        }

        attributes = Node.objects.filter(pk=id)
        serializer = PointSerializer(attributes, many=True, context=serializer_context)
        serializer_points = {}
        serializer_ways = {}

        type = 'NODE'
        if not attributes:
            attributes = Way.objects.filter(pk=id)
            serializer = WaySerializer(attributes, many=True, context=serializer_context)

            points = Node.objects.filter(way_reference=id)
            serializer_points = PointSerializer(points, many=True, context=serializer_context).data
            serializer_ways = {}

            type = 'WAY'

        if not attributes:
            attributes = Relation.objects.filter(pk=id)
            serializer = RelationSerializer(attributes, many=True)

            points = Node.objects.filter(relation_reference=id)
            serializer_points = PointSerializer(points, many=True, context=serializer_context).data

            ways = Way.objects.filter(relation_reference=id)
            serializer_ways = WaySerializer(ways, many=True, context=serializer_context).data

            type = 'RELATION'

        if not attributes:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        serializer_tag = {}
        try:

            tag_list = Tag.objects.filter(reference=id)
            serializer_tag = TagSerializer(tag_list, many=True)
        except Tag.DoesNotExist:
            pass

        entity = {
            'type': type,
            'attributes': serializer.data,
            'serializer_points': serializer_points,
            'serializer_ways': serializer_ways,
            'tag_list': serializer_tag.data
        }

        return Response(entity, status=status.HTTP_200_OK)


class CorrespondenceInvalideView(viewsets.ViewSet):
    def list(self, request, format=None):

        # http://127.0.0.1:8000/correspondence-invalide/?osm=194554955&gn=822469
        if request.GET.get('osm') and request.GET.get('gn'):
            try:
                correspondence = CorrespondenceInvalide.objects.get(reference_osm=int(request.GET.get('osm')),
                                                                    reference_gn=int(request.GET.get('gn')))
            except CorrespondenceInvalide.DoesNotExist:
                return Response(status=status.HTTP_400_BAD_REQUEST)

            serializer = CorrespondenceInvalideSerializer(correspondence)

        else:
            # http://127.0.0.1:8000/correspondence-invalide
            correspondences = CorrespondenceInvalide.objects.all()
            serializer = CorrespondenceInvalideSerializer(correspondences, many=True)

        return Response(serializer.data)

    def post(self, request, format=None):

        print(request.data)
        serializer = CorrespondenceInvalideSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()

            CorrespondenceEntity.objects.filter(reference_gn=request.data['reference_gn'],
                                                reference_osm=request.data['reference_osm']).update(validation=INVALIDE)

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CorrespondenceTypesViewSet(viewsets.ModelViewSet):
    # TODO: Help pour visualizer... blablabla

    queryset = CorrespondenceTypes.objects.all()
    serializer_class = CorrespondenceTypesSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


class CorrespondenceTypesCloseViewSet(viewsets.ModelViewSet):
    queryset = CorrespondenceTypesClose.objects.all()
    serializer_class = CorrespondenceTypesCloseSerializer


class ScheduledWorkViewSet(viewsets.ModelViewSet):
    queryset = ScheduledWork.objects.all()
    serializer_class = ScheduledWorkSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def create(self, request, **kwargs):
        request.data['process_id'] = random.randint(1, 100)
        serializer = ScheduledWorkSerializer(data=request.data)

        if request.data.get('name', '') == SCHEDULED_WORK_IMPORTATION_PROCESS and not request.data.get('country_name'):
            raise Exception("Country name parameter required")

        if request.data.get('name', '') == SCHEDULED_WORK_IMPORTATION_PROCESS:
            count = CountryImported.objects.filter(country_name=request.data.get('country_name', '').upper()).count()
            if count > 0:
                raise Exception("The country had already imported")
            else:
                country_imported = CountryImported(country_name=request.data.get('country_name'))
                country_imported.save()

        if serializer.is_valid():
            serializer.save()

            thread = BackgroundProcess(thread_id=request.data.get('process_id'), name=request.data.get('name'),
                                       process=request.data.get('name'),
                                       positional_params=request.data.get('file_name'),
                                       others_params='skip_geonames')
            thread.start()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CountryImportedView(mixins.ListModelMixin, mixins.RetrieveModelMixin,
                          viewsets.GenericViewSet):
    queryset = CountryImported.objects.all()
    serializer_class = CountryImportedSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
