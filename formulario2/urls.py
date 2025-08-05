from django.urls import path
from .views import (
    home_view, Formulario2CreateView, Formulario2ListView,
    FormularioAmilCreateView, FormularioAmilListView,
    CustomLoginView, CustomLogoutView
)

urlpatterns = [
    # Login/Logout
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    
    # Página inicial
    path('', home_view, name='home'),
    
    # Formulário Porto Seguro
    path('porto/create/', Formulario2CreateView.as_view(), name='formulario2_create'),
    path('porto/', Formulario2ListView.as_view(), name='formulario2_list'),
    
    # Formulário Amil
    path('amil/create/', FormularioAmilCreateView.as_view(), name='formulario_amil_create'),
    path('amil/', FormularioAmilListView.as_view(), name='formulario_amil_list'),
] 