"""
URL configuration for formulario project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from formulario2.views import (
    Formulario2APIView, Formulario2DetailAPIView,
    FormularioAmilAPIView, FormularioAmilDetailAPIView
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('formulario2/', include('formulario2.urls')),
    
    # API Endpoints - Formulario2 (Porto)
    path('api/porto/', Formulario2APIView.as_view(), name='formulario2_api'),
    path('api/porto/<int:pk>/', Formulario2DetailAPIView.as_view(), name='formulario2_detail_api'),
    
    # API Endpoints - FormularioAmil
    path('api/amil/', FormularioAmilAPIView.as_view(), name='formulario_amil_api'),
    path('api/amil/<int:pk>/', FormularioAmilDetailAPIView.as_view(), name='formulario_amil_detail_api'),
]
