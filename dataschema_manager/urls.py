from django.conf.urls import url
from django.contrib.auth.decorators import login_required


from .views import DataSchemaOverview
from .views import dataschema_new
from .views import dataschema_edit
from .views import dataschema_write

urlpatterns = [
    url(r'^new/field/(?P<experiment_id>\d+)$', dataschema_new, name="dataschemafield_new"),
    url(r'^edit/field/(?P<pk>\d+)/(?P<experiment_id>\d+)$', dataschema_edit, name="dataschemafield_edit"),
    url(r'^write/field/(?P<experiment_id>\d+)$', dataschema_write, name="dataschema_write"),
]
