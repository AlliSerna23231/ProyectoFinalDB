from django.urls import path
from . import views

urlpatterns = [
    path('', views.registro, name='registro'),
    path('inicio_sesion/', views.iniciosesion, name='iniciosesion'),
    path('home/', views.home, name='home'),
    path('cerrar_sesion/', views.cerrar_sesion, name='cerrar_sesion'),  
    path('publicacion/', views.publicar, name='publicar'),
    path('mostrar_publicacion/', views.mostrar_publicacion, name='mostrar_publicacion'),
    path('buscar_amigos/', views.buscar_amigos, name='buscar_amigos'),
    path('ver_perfil/<int:id_us>/', views.ver_perfil, name='ver_perfil'),
    path('chatear/<int:id_us>/', views.chatear, name='chatear'),
    path('enviar_mensaje/<int:id_us>/', views.enviar_mensaje, name='enviar_mensaje'),







]
