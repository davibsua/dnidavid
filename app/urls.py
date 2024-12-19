from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login, name='login'),
    path('registro/', views.registro, name='registro'),
    path('logout/', views.logout, name='logout'),
    path('ingreso/', views.ingreso, name='ingreso'),
    path('retiro/', views.retiro, name='retiro'),
    path('ingreso_programado/', views.ingreso_programado, name='ingreso_programado'),
    path('retiro_programado/', views.retiro_programado, name='retiro_programado'),
    path('movimientos/', views.movimientos, name='movimientos'),
    path('datos/', views.datos, name='datos'),
]
