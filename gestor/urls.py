from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from gestor.views import ProyectoExplorerView, ProyectoDataAPIView

urlpatterns = [
    path('explorer/', ProyectoExplorerView.as_view(), name='proyecto_explorer'),
    path('proyecto-data/', ProyectoDataAPIView.as_view(), name='proyecto_data_api'),

]
