from reportapp.apps import ReportappConfig
from django.urls import path
from reportapp import views

app_name = ReportappConfig.name

urlpatterns = [
    path('upload/', views.upload, name='upload'),
    path('', views.ContactCenterView.as_view(), name='home'),
    path('<int:pk>/detail_cc/', views.ContactCenterDetailView.as_view(), name='center_detail'),
    path('<int:pk>/group/', views.GroupView.as_view(), name='group'),
    path('<int:pk>/group_detail/', views.group_detail_view, name='group_detail')
]
