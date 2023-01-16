from reportapp.apps import ReportappConfig
from django.urls import path
from reportapp import views

app_name = ReportappConfig.name

urlpatterns = [
    path('upload/', views.upload, name='upload'),
    path('', views.ContactCenterView.as_view(), name='home'),
    path('<int:pk>/detail_cc/', views.ContactCenterDetailView.as_view(), name='center_detail'),
    path('<int:pk>/group/', views.GroupView.as_view(), name='group'),
    path('<int:pk>/group_detail/', views.GroupDetailView.as_view(), name='group_detail'),
    path('<int:pk>/employee/', views.EmployeeView.as_view(), name='employee'),
    path('<str:name>/employee_detail/', views.EmployeeDetailView.as_view(), name='employee_detail'),
    path('leaders/', views.RatingLeaders.as_view(), name='leaders'),
    path("log_view/", views.LogView.as_view(), name="log_view"),
    path("log_download/", views.LogDownloadView.as_view(), name="log_download"),
]
