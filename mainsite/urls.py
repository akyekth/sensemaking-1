from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.DashboardView.as_view(), name='index'),
    url(r'^home/$', views.DashboardView.as_view(), name='index'),
    url(r'^plot_search', views.DashboardView.as_view(), name='index'),
    url(r'^search', views.DashboardView.as_view(), name='index'),
    url(r'^advancedsearch', views.DashboardView.as_view(), name='index'),
    url(r'^tweets', views.DashboardView.as_view(), name='index'),
    url(r'^virality-prediction/$', views.ViralityPredictionView.as_view(), name='virality-prediction'),
    url(r'^filterhashtags', views.ViralityPredictionView.as_view(), name='virality-prediction'),
    url(r'^predictcascades', views.ViralityPredictionView.as_view(), name='prediction'),
]