"""TER URL Configuration
--------------------------

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken import views as authviews
from services import views


router = DefaultRouter(trailing_slash=False)
router.register(r'tags', views.TagViewSet)
router.register(r'points', views.PointViewSet)
router.register(r'ways', views.WayViewSet)
router.register(r'relations', views.RelationViewSet)
router.register(r'geonames', views.GeonamesViewSet)
router.register(r'feature-code', views.FeatureCodeViewSet)
router.register(r'parameters', views.ParametersViewSet)
router.register(r'parameters-score-pertinence', views.ParametersScorePertinenceViewSet)
router.register(r'parameters-score-pertinence-history', views.ParametersScorePertinenceHistoryViewSet)
router.register(r'entity-osm-details/(?P<id>.+)/$', views.EntityOSMDetails, base_name='entity-osm-details')

router.register(r'correspondence', views.CorrespondenceEntityView, base_name='correspondence')
router.register(r'correspondence-types', views.CorrespondenceTypesViewSet)
router.register(r'correspondence-types-close', views.CorrespondenceTypesCloseViewSet)
router.register(r'correspondence-invalid-type', views.CorrespondenceTypesInvalidViewSet)
router.register(r'correspondence-valide', views.CorrespondenceValideView, base_name='correspondence-valide')
router.register(r'correspondence-invalide', views.CorrespondenceInvalideView,  base_name='correspondence-invalide')
router.register(r'scheduled-work', views.ScheduledWorkViewSet)
router.register(r'country-imported', views.CountryImportedView)


urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^admin/', admin.site.urls),
    url(r'^api-auth/',include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api-token-auth/', authviews.obtain_auth_token)
]