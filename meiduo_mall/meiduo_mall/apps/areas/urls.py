from django.conf.urls import url
from rest_framework.routers import DefaultRouter
from . import views


urlpatterns = [
    # url(r'^areas/$', views.AreaListView.as_view()),
    # url(r'^areas/(?P<pk>\d+)/$', views.SubAreaListView.as_view()),
]

router = DefaultRouter()
router.register('areas', views.AreaViewSet, base_name='areas')
urlpatterns += router.urls