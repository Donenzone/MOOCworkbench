from django.conf.urls import url

from .views import dataschema_overview
from .views import dataschema_new
from .views import dataschema_edit
from .views import dataschema_write

urlpatterns = [
    url(r'^overview/(?P<experiment_id>\d+)$', dataschema_overview, name="dataschema_overview"),
    url(r'^new/field/(?P<experiment_id>\d+)$', dataschema_new, name="dataschemafield_new"),
    url(r'^edit/field/(?P<pk>\d+)/(?P<experiment_id>\d+)$', dataschema_edit, name="dataschemafield_edit"),
    url(r'^write/field/(?P<experiment_id>\d+)$', dataschema_write, name="dataschema_write"),
]
