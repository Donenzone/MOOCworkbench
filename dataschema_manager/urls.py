from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from .views import DataSchemaFieldCreateView
from .views import dataschema_edit

urlpatterns = [
    url(r'^new/field/(?P<experiment_id>\d+)$', login_required(DataSchemaFieldCreateView.as_view()), name="dataschemafield_new"),
    url(r'^edit/field/(?P<pk>\d+)$', dataschema_edit, name="dataschemafield_edit"),
]
