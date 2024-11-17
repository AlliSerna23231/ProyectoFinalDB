from django.urls import path
from . import views

urlpatterns = [
    path('', views.registro, name='registro'),
    path('inicio_sesion/', views.iniciosesion, name='iniciosesion'),
    path('home/', views.home, name='home'),
    path('cerrar_sesion/', views.cerrar_sesion, name='cerrar_sesion'),  
    path('publicacion/', views.publicar, name='publicar')


]
