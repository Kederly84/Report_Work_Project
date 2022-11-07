from reportapp.apps import ReportappConfig
from django.urls import path
from reportapp import views

app_name = ReportappConfig.name

urlpatterns = [
    path('', views.home, name='home'),
    path('upload/', views.upload, name='upload'),
    path('report/', views.ContactCenterView.as_view(), name='report')
]
