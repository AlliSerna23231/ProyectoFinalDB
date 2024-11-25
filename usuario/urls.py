from django.urls import path
from . import views

urlpatterns = [
    path('', views.registro, name='registro'),
    path('inicio_sesion/', views.iniciosesion, name='iniciosesion'),
    path('home/', views.home, name='home'),
    path('cerrar_sesion/', views.cerrar_sesion, name='cerrar_sesion'),  
    path('publicacion/', views.publicar, name='publicar'),
    path('mostrar_publicacion/', views.mostrar_publicacion, name='mostrar_publicacion'),
    path('me_gusta/<int:id_publicacion>/', views.me_gusta, name='me_gusta'),
    path('contador_me_gusta/<int:id_publicacion>/', views.contador_me_gusta, name='contador_me_gusta'),
    path('me_gustapublicacion/<int:id_publicacion>/', views.me_gustapublicacion, name='me_gustapublicacion'),
    path('contadorme_gustapublicacion/<int:id_publicacion>/', views.contadorme_gustapublicacion, name='contadorme_gustapublicacion'),
    path('comentar/<int:id_publicacion>/', views.comentar, name='comentar'),
    path('comentarios/<int:id_publicacion>/', views.comentarios, name='comentarios'),
    path('usuarios/', views.usuarios, name='usuarios'),
    path('filtros/', views.filtros, name='filtros'),
    path('ver_perfil/<int:id_us>/', views.ver_perfil, name='ver_perfil'),
    path('me_gustaperfil/<int:id_publicacion>/', views.me_gustaperfil, name='me_gustaperfil'),
    path('contadorme_gustaperfil/<int:id_publicacion>/', views.contadorme_gustaperfil, name='contadorme_gustaperfil'),
    path('chatear/<int:id_us>/', views.chatear, name='chatear'),
    path('enviar_mensaje/<int:id_us>/', views.enviar_mensaje, name='enviar_mensaje'),
    path('addamigo/<int:id_us>/', views.addamigo, name='addamigo'),
    path('buscar_amigos/', views.buscar_amigos, name='buscar_amigos'),
    path('publicaciones/', views.publicaciones, name='publicaciones'),










]
