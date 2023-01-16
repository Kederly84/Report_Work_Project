import datetime
import logging
import os

from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.db.models import Avg, Sum
from django.shortcuts import render
from django.utils.safestring import mark_safe
from django.views.generic import TemplateView

from config.settings import MEDIA_ROOT
from reportapp.models import ReportData, Area
from reportapp.services.report_services import contact_center_detail_service, group_detail_service, dates_parse, \
    employee_detail_service, rating_leaders
from reportapp.task import insert_data

logger = logging.getLogger(__name__)


FLAGS = {
    'CC main view': 'cc main view',
    'CC detail view': 'cc detail view',
    'Group main view': 'group main view',
    'Group detail view': 'group detail view',
    'Employee view': 'employee view',
    'Employee detail view': 'employee detail view'
}


def upload(request):
    if request.method == 'POST' and request.FILES and len(os.listdir(MEDIA_ROOT)) == 0:
        if request.FILES['upload']:
            upload_file = request.FILES['upload']
            if upload_file.name.endswith('.csv'):
                fss = FileSystemStorage()
                fss.save(upload_file.name, upload_file)
                insert_data(upload_file.name)
            else:
                messages.add_message(request, messages.WARNING,
                                     mark_safe("Неверный формат файла"))
    elif request.method == 'POST' and request.POST.get('delete') == 'Delete':
        for f in os.listdir(MEDIA_ROOT):
            os.remove(os.path.join(MEDIA_ROOT, f))
    with os.scandir(MEDIA_ROOT) as entries:
        file_url = ''
        for entry in entries:
            if entry.is_file():
                file_url += entry.name
    return render(request, 'reportapp/upload.html', {'file_url': file_url})


class ContactCenterView(TemplateView):
    template_name = 'reportapp/report.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        date = ReportData.objects.order_by('-date').values('date').first()
        if date:
            date = date['date'].strftime('%Y-%m-%d')
        else:
            return context
        context['data'] = ReportData.objects.filter(date=date, job__calculated=True).values('contact_center',
                                                                                            'contact_center__area_name').annotate(
            scheduled_time_sum=Sum('scheduled_time'),
            ready_sum=Sum('ready'),
            rating_avg=Avg('rating'),
            adherence_avg=Avg('adherence'),
            sick_leave_sum=Sum('sick_leave'),
            absenteeism_sum=Sum('absenteeism'))
        context['flag'] = FLAGS['CC main view']
        context['cc_list'] = Area.objects.filter(deleted=False)
        return context


class ContactCenterDetailView(TemplateView):
    template_name = 'reportapp/report.html'

    def get_context_data(self, **kwargs):
        context = super(ContactCenterDetailView, self).get_context_data(**kwargs)
        date = ReportData.objects.order_by('-date').values('date').first()
        if date:
            date = date['date'].strftime('%Y-%m-%d')
        else:
            return context
        context['data'] = ReportData.objects.filter(contact_center=kwargs['pk'], date=date,
                                                    job__calculated=True).values(
            'date',
            'contact_center__area_name', 'contact_center').annotate(
            scheduled_time_sum=Sum('scheduled_time'),
            ready_sum=Sum('ready'),
            rating_avg=Avg('rating'),
            adherence_avg=Avg('adherence'),
            sick_leave_sum=Sum('sick_leave'),
            absenteeism_sum=Sum('absenteeism'))
        context['date'] = ReportData.objects.order_by('date').values('date').filter(
            contact_center=kwargs['pk']).distinct()
        context['contact_center_name'] = ReportData.objects.filter(contact_center=self.kwargs.get('pk')).values(
            'contact_center__area_name').first()
        context['flag'] = FLAGS['CC detail view']
        context['cc_list'] = Area.objects.filter(deleted=False)
        return context

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        start, end = dates_parse(request)
        context['data'] = contact_center_detail_service(kwargs['pk'], start, end)
        context['date'] = ReportData.objects.order_by('date').values('date').filter(
            contact_center=self.kwargs.get('pk')).distinct()
        return self.render_to_response(context)


class GroupView(TemplateView):
    template_name = 'reportapp/report.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        date = ReportData.objects.order_by('-date').values('date').first()
        if date:
            date = date['date'].strftime('%Y-%m-%d')
        else:
            return context
        context['data'] = ReportData.objects.filter(contact_center=self.kwargs.get('pk'),
                                                    date=date, job__calculated=True).values('group',
                                                                                            'group__group_name').annotate(
            scheduled_time_sum=Sum('scheduled_time'),
            ready_sum=Sum('ready'),
            rating_avg=Avg('rating'),
            adherence_avg=Avg('adherence'),
            sick_leave_sum=Sum('sick_leave'),
            absenteeism_sum=Sum('absenteeism')).order_by('group')
        context['flag'] = FLAGS['Group main view']
        return context


class GroupDetailView(TemplateView):
    template_name = 'reportapp/report.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        date = ReportData.objects.order_by('-date').values('date').first()
        if date:
            date = date['date'].strftime('%Y-%m-%d')
        else:
            return context
        context['data'] = ReportData.objects.filter(group=self.kwargs.get('pk'),
                                                    date=date, job__calculated=True).values('date',
                                                                                            'group__group_name',
                                                                                            'group').annotate(
            scheduled_time_sum=Sum('scheduled_time'),
            ready_sum=Sum('ready'),
            rating_avg=Avg('rating'),
            adherence_avg=Avg('adherence'),
            sick_leave_sum=Sum('sick_leave'),
            absenteeism_sum=Sum('absenteeism'))
        context['date'] = ReportData.objects.order_by('date').values('date').filter(
            group=self.kwargs.get('pk')).distinct()
        context['flag'] = FLAGS['Group detail view']
        contact_center = ReportData.objects.filter(group=self.kwargs.get('pk')).first().contact_center
        context['group_list'] = ReportData.objects.order_by('group').values(
            'group', 'group__group_name').filter(contact_center=contact_center).distinct()
        return context

    def post(self, request, **kwargs):
        context = self.get_context_data(**kwargs)
        start, end = dates_parse(request)
        context['data'] = group_detail_service(self.kwargs.get('pk'), start, end)
        context['date'] = ReportData.objects.order_by('date').values('date').filter(
            group=self.kwargs.get('pk')).distinct()
        context['gr_name'] = ReportData.objects.filter(group=self.kwargs.get('pk')).values('group__group_name').first()
        return self.render_to_response(context)


# def group_detail_view(request, pk):
#     start, end = data_parse(request)
#     print(start, end)
#     data = group_detail_service(pk, start, end)
#     date = ReportData.objects.order_by('date').values('date').filter(group=pk).distinct()
#     gr_name = ReportData.objects.filter(group=pk).values('group__group_name').first()
#     print(data)
#     return render(request, 'reportapp/report.html',
#                   {'data': data, 'date': date, 'gr_name': gr_name})
#
# def group_view(request, pk):
#     if request.method == 'POST':
#         try:
#             start_date_check = datetime.strptime(request.POST.get('start_date'), '%Y-%m-%d')
#             end_date_check = datetime.strptime(request.POST.get('end_date'), '%Y-%m-%d')
#             if end_date_check >= start_date_check:
#                 start_date = request.POST.get('start_date')
#                 end_date = request.POST.get('end_date')
#                 data = contact_center_detail_service(pk, start_date, end_date)
#             else:
#                 data = contact_center_detail_service(pk)
#                 messages.add_message(request, messages.WARNING,
#                                      mark_safe("Конечная дата не может быть меньше начальной"))
#         except ValueError:
#             data = contact_center_detail_service(pk)
#             messages.add_message(request, messages.WARNING, mark_safe("Выберите дату начала и дату конца периода"))
#     else:
#         data = contact_center_detail_service(pk)
#     date = ReportData.objects.order_by('date').values('date').filter(
#         contact_center=pk).distinct()
#     contact_center_name = ReportData.objects.filter(contact_center=pk).values('contact_center__area_name').first()
#     print(data)
#     return render(request, 'reportapp/report.html',
#                   {'data': data, 'date': date, 'contact_center_name': contact_center_name})

class EmployeeView(TemplateView):
    template_name = 'reportapp/report.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        date = ReportData.objects.order_by('-date').values('date').first()
        if date:
            date = date['date'].strftime('%Y-%m-%d')
        else:
            return context
        context['data'] = ReportData.objects.filter(group=self.kwargs.get('pk'),
                                                    date=date, job__calculated=True
                                                    ).values('date',
                                                             'full_name',
                                                             'group__group_name').annotate(
            scheduled_time_sum=Sum('scheduled_time'),
            ready_sum=Sum('ready'),
            rating_avg=Avg('rating'),
            adherence_avg=Avg('adherence'),
            sick_leave_sum=Sum('sick_leave'),
            absenteeism_sum=Sum('absenteeism'))
        context['flag'] = FLAGS['Employee view']
        return context


class EmployeeDetailView(TemplateView):
    template_name = 'reportapp/report.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        date = ReportData.objects.order_by('-date').values('date').first()
        if date:
            date = date['date'].strftime('%Y-%m-%d')
        else:
            return context
        context['data'] = ReportData.objects.filter(full_name=self.kwargs.get('name'),
                                                    date=date).values('date').annotate(
            scheduled_time_sum=Sum('scheduled_time'),
            ready_sum=Sum('ready'),
            rating_avg=Avg('rating'),
            adherence_avg=Avg('adherence'),
            sick_leave_sum=Sum('sick_leave'),
            absenteeism_sum=Sum('absenteeism'))
        context['flag'] = FLAGS['Employee detail view']
        context['date'] = ReportData.objects.order_by('date').values('date').filter(
            full_name=self.kwargs.get('name')).distinct()
        return context

    def post(self, request, **kwargs):
        context = self.get_context_data(**kwargs)
        start, end = dates_parse(request)
        context['data'] = employee_detail_service(self.kwargs.get('name'), start, end)
        context['date'] = ReportData.objects.order_by('date').values('date').filter(
            full_name=self.kwargs.get('name')).distinct()
        return self.render_to_response(context)


class RatingLeaders(TemplateView):
    template_name = 'reportapp/leaders.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        date = ReportData.objects.order_by('-date').values('date').first()
        if date:
            date = date['date'].strftime('%Y-%m-%d')
        else:
            return context
        leaders = ReportData.objects.order_by('-rating').filter(date=date).values('full_name', 'rating', 'date')[
                  :100]
        context['date'] = ReportData.objects.order_by('-date').values('date').distinct()
        context['data'] = rating_leaders(leaders)
        context['date_label'] = datetime.datetime.strptime(date, '%Y-%m-%d')
        return context

    def post(self, request, **kwargs):
        context = self.get_context_data(**kwargs)
        try:
            date_check = datetime.datetime.strptime(request.POST.get('leaders_date'), '%Y-%m-%d')
            if date_check:
                date_check = request.POST.get('leaders_date')
                leaders = ReportData.objects.order_by('-rating').filter(date=date_check).values('full_name',
                                                                                                'rating',
                                                                                                'date')[:100]
                context['data'] = rating_leaders(leaders)
                context['date_label'] = datetime.datetime.strptime(date_check, '%Y-%m-%d')
            else:
                messages.add_message(request, messages.WARNING,
                                     mark_safe("Выберите дату"))
        except ValueError:
            messages.add_message(request, messages.WARNING, mark_safe("Выберите дату"))
        return self.render_to_response(context)
