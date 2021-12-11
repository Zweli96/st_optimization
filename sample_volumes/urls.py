from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.loginPage, name="login"),
    path('logout/', views.logoutUser, name="logout"),
    path('register/', views.registerUser, name="register"),
    path('volumes/', views.dashboard, name="home"),
    path('volumes/<str:pk>/', views.dashboard, name="home"),
    path('sample_volumes/', views.sample_volumes, name="sample_volumes"),
    path('couriers/', views.couriers, name="couriers"),
    path('districts/', views.districts, name="districts"),
    path('create_district/', views.createDistrict, name="create_district"),
    path('update_district/<str:pk>/',
         views.updateDistrict, name="update_district"),
    path('delete_district/<str:pk>/',
         views.deleteDistrict, name="delete_district"),
    path('facilities/', views.facilities, name="facilities"),
    path('create_facility/', views.createFacility, name="create_facility"),
    path('update_facility/<str:pk>/',
         views.updateFacility, name="update_facility"),
    path('delete_facility/<str:pk>/',
         views.deleteFacility, name="delete_facility"),
    path('health_workers/', views.health_workers, name="health_workers"),
    path('create_health_worker/', views.createHealth_Worker,
         name="create_health_worker"),
    path('update_health_worker/<str:pk>/',
         views.updateHealth_Worker, name="update_health_worker"),
    path('delete_health_worker/<str:pk>/',
         views.deleteHealth_Worker, name="delete_health_worker"),
    path('make_routes/', views.makeRoutes, name="make_routes"),

]
