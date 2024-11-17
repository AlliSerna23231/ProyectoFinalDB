from django.urls import path
from . import views

urlpatterns = [
    path('', views.registro, name='registro'),
    path('inicio_sesion/', views.iniciosesion, name='iniciosesion'),
    path('home/', views.home, name='home'),

]
