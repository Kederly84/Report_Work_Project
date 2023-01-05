import os
from datetime import datetime

from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.db.models import Avg, Sum
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.utils.safestring import mark_safe
from django.views.generic import TemplateView

from config.settings import MEDIA_ROOT
from reportapp.models import ReportData, Area
from reportapp.services.report_services import contact_center_detail_service, group_detail_service, data_parse
from reportapp.task import insert_data

FLAGS = {
    'CC main view': 'CC main view',
    'CC detail view': 'CC detail view',
    'Group main view': 'Group main view',

}
# ToDo: Magic number приводит год к текущему - убрать перед размещением
CURR_YEAR = datetime.now().year - 1


def home(request):
    return render(request, 'reportapp/home.html')


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
        date = ReportData.objects.order_by('-date').values('date').first()
        if date:
            date = date['date'].strftime('%Y-%m-%d')
        else:
            return context
        context['data'] = ReportData.objects.filter(date=date, date__year=CURR_YEAR).values('contact_center',
                                                                                            'contact_center__area_name').annotate(
            scheduled_time_sum=Sum('scheduled_time'),
            ready_sum=Sum('ready'),
            rating_avg=Avg('rating'),
            adherence_avg=Avg('adherence'),
            sick_leave_sum=Sum('sick_leave'),
            absenteeism_sum=Sum('absenteeism'))
        context['flag'] = 'contact center'
        return context


# ToDo: Переписать представление с фильтрацией по дате как в GroupView и избавиться от глобальной переменной CURR_YEAR
class ContactCenterDetailView(TemplateView):
    template_name = 'reportapp/report.html'

    def get_context_data(self, **kwargs):
        context = super(ContactCenterDetailView, self).get_context_data(**kwargs)
        context['data'] = ReportData.objects.filter(contact_center=kwargs['pk'], date__year=CURR_YEAR).values(
            'date',
            'contact_center__area_name').annotate(
            scheduled_time_sum=Sum('scheduled_time'),
            ready_sum=Sum('ready'),
            rating_avg=Avg('rating'),
            adherence_avg=Avg('adherence'),
            sick_leave_sum=Sum('sick_leave'),
            absenteeism_sum=Sum('absenteeism'))
        context['date'] = ReportData.objects.order_by('date').values('date').filter(
            contact_center=kwargs['pk']).distinct()
        return context

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        if request.method == 'POST':
            try:
                start_date_check = datetime.strptime(request.POST.get('start_date'), '%Y-%m-%d')
                end_date_check = datetime.strptime(request.POST.get('end_date'), '%Y-%m-%d')
                if end_date_check >= start_date_check:
                    start_date = request.POST.get('start_date')
                    end_date = request.POST.get('end_date')
                    context['data'] = contact_center_detail_service(kwargs['pk'], start_date, end_date)
                else:
                    messages.add_message(request, messages.WARNING,
                                         mark_safe("Конечная дата не может быть меньше начальной"))
            except ValueError:
                messages.add_message(request, messages.WARNING, mark_safe("Выберите дату начала и дату конца периода"))
        return self.render_to_response(context)


# def contact_center_detail(request, pk):
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
#     return render(request, 'reportapp/report.html',
#                   {'data': data, 'date': date, 'contact_center_name': contact_center_name, 'flag': 'C'})


class GroupView(TemplateView):
    template_name = 'reportapp/report.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        date = ReportData.objects.order_by('-date').values('date').first()
        if date:
            date = date['date'].strftime('%Y-%m-%d')
        else:
            return context
        context['contact_center'] = get_object_or_404(Area, pk=self.kwargs.get('pk'))
        context['data'] = ReportData.objects.filter(contact_center=context['contact_center'],
                                                    date=date).values('group',
                                                                      'group__group_name').annotate(
            scheduled_time_sum=Sum('scheduled_time'),
            ready_sum=Sum('ready'),
            rating_avg=Avg('rating'),
            adherence_avg=Avg('adherence'),
            sick_leave_sum=Sum('sick_leave'),
            absenteeism_sum=Sum('absenteeism'))
        context['contact_center_name'] = ReportData.objects.values('contact_center__area_name')
        print(context)
        return context


def group_detail_view(request, pk):
    start, end = data_parse(request)
    print(start, end)
    data = group_detail_service(pk, start, end)
    date = ReportData.objects.order_by('date').values('date').filter(group=pk).distinct()
    gr_name = ReportData.objects.filter(group=pk).values('group__group_name').first()
    print(data)
    return render(request, 'reportapp/report.html',
                  {'data': data, 'date': date, 'gr_name': gr_name})

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
