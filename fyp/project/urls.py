from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'project'

urlpatterns = [
    path('new', views.ProjectCreateView, name='create'),
    path('list',views.ProjectListView.as_view(), name='list'),
    path('plot/<int:pk>/',views.plotGraph, name='create-plot'),
    path('read/<int:pk>', views.read_data, name='read'),
    path('<int:pk>/', views.plotList, name='plot-list'),
    path('<int:pk>/<int:plotpk>/', views.viewPlot, name='view-plot'),
    path('dashboard/<int:pk>/', views.dashboard, name='dashboard'),
    path('<int:pk>/delete/', views.projectDeleteView.as_view(), name='project-delete'),
    path('plot/<int:pk>/delete/', views.plotDeleteView.as_view(), name='plot-delete'),
    # path('graph/<int:pk>/',views.get_data, name="test")
]
