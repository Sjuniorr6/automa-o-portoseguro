from django.urls import path
from .views import (
    home_view, Formulario2CreateView, Formulario2ListView,
    FormularioAmilCreateView, FormularioAmilListView,
    api_viewer, AutomationLogListView
)

urlpatterns = [
    path('', home_view, name='home'),
    path('porto/', Formulario2ListView.as_view(), name='formulario2_list'),
    path('porto/create/', Formulario2CreateView.as_view(), name='formulario2_create'),
    path('amil/', FormularioAmilListView.as_view(), name='formulario_amil_list'),
    path('amil/create/', FormularioAmilCreateView.as_view(), name='formulario_amil_create'),
    path('api-viewer/', api_viewer, name='formulario2_api_viewer'),
    path('automation-logs/', AutomationLogListView.as_view(), name='automation_logs'),
] 