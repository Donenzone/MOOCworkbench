from django.conf.urls import url

from .views import (dataschemafield_edit, dataschemafield_new,
                    dataschema_write)

urlpatterns = [
    url(r'^new/field/(?P<experiment_id>\d+)$', dataschemafield_new, name="dataschemafield_new"),
    url(r'^edit/field/(?P<pk>\d+)/(?P<experiment_id>\d+)$', dataschemafield_edit, name="dataschemafield_edit"),
    url(r'^write/field/(?P<experiment_id>\d+)$', dataschema_write, name="dataschema_write"),
]
