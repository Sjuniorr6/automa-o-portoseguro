from django.urls import path
from .views import Formulario2CreateView, Formulario2ListView, Formulario2APIView, Formulario2DetailAPIView, api_viewer, AutomationLogListView

urlpatterns = [
    path('', Formulario2ListView.as_view(), name='formulario2_list'),
    path('create/', Formulario2CreateView.as_view(), name='formulario2_create'),
    path('api-viewer/', api_viewer, name='formulario2_api_viewer'),
    path('automation-logs/', AutomationLogListView.as_view(), name='automation_logs'),
    
    # API Endpoints
    path('api/', Formulario2APIView.as_view(), name='formulario2_api'),
    path('api/<int:pk>/', Formulario2DetailAPIView.as_view(), name='formulario2_detail_api'),
] 