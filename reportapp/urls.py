from reportapp.apps import ReportappConfig
from django.urls import path
from reportapp import views

app_name = ReportappConfig.name

urlpatterns = [
    path('upload/', views.upload, name='upload'),
    path('', views.ContactCenterView.as_view(), name='home'),
    path('<int:pk>/detail_cc/', views.contact_center_detail, name='center_detail'),
    path('<int:pk>/group/', views.GroupView.as_view(), name='group')
]
