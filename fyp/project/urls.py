from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'project'

urlpatterns = [
    path('new', views.ProjectCreateView, name='create'),
    path('list',views.ProjectListView.as_view(), name='list'),
    path('<int:pk>/',views.plotGraph, name='plot' )
]
