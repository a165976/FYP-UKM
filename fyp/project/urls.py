from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'project'

urlpatterns = [
    path('new', views.ProjectCreateView.as_view(), name='create'),
    path('list',views.ProjectListView.as_view(), name='list'),
]
