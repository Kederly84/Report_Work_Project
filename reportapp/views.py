import os

from django.core.files.storage import FileSystemStorage
from django.shortcuts import render
from django.views.generic import TemplateView
from django.db.models import Avg, Sum, Subquery

from config.settings import MEDIA_ROOT
from reportapp.task import insert_data
from reportapp.models import ReportData
from reportapp.services.report_services import contact_center_service


def home(request):
    return render(request, 'reportapp/home.html')


def upload(request):
    if request.method == 'POST' and request.FILES and len(os.listdir(MEDIA_ROOT)) == 0:
        if request.FILES['upload']:
            upload_file = request.FILES['upload']
            fss = FileSystemStorage()
            fss.save(upload_file.name, upload_file)
            insert_data(upload_file.name)
    elif request.method == 'POST' and request.POST.get('delete') == 'Delete':
        for f in os.listdir(MEDIA_ROOT):
            os.remove(os.path.join(MEDIA_ROOT, f))
    with os.scandir(MEDIA_ROOT) as entries:
        file_url = ''
        for entry in entries:
            if entry.is_file():
                file_url += entry.name
    return render(request, 'reportapp/upload.html', {'file_url': file_url})


# class GroupDetailView(TemplateView):
#     template_name = 'reportapp/group_detail.html'
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         if self.kwargs.get('data'):
#             date = self.kwargs.get('data')
#         else:
#             date = ReportData.objects.order_by('date').values('date').first()
#             date = date['date'].strftime('%Y-%m-%d')
#         context['employees'] = ReportData.objects.filter(date=date).filter(group=self.kwargs.get('group'))
#         context['dates'] = ReportData.objects.order_by().values('date').distinct()
#         return context


class ContactCenterView(TemplateView):
    template_name = 'reportapp/report.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.kwargs.get('data'):
            date = self.kwargs.get('data')
        else:
            date = ReportData.objects.order_by('-date').values('date').first()
            date = date['date'].strftime('%Y-%m-%d')
        # context['data'] = contact_center_service(date)
        context['data'] = ReportData.objects.filter(date=date).values('contact_center__area_name').annotate(
            scheduled_time_sum=Sum('scheduled_time'),
            ready_sum=Sum('ready'),
            share_ready_avg=Avg('share_ready'),
            adherence_avg=Avg('adherence'),
            sick_leave_sum=Sum('sick_leave'),
            absenteeism_sum=Sum('absenteeism'))
        # print(context['data'])
        return context
