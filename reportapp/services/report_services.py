from datetime import datetime

from django.contrib import messages
from django.db.models import Avg, Sum
from django.utils.safestring import mark_safe

from reportapp.models import ReportData


def contact_center_detail_service(pk: int, start_date: str = None, end_date: str = None):
    if start_date and end_date:
        data = ReportData.objects.filter(contact_center=pk,
                                         date__range=[start_date, end_date], job__calculated=True).values(
            'date',
            'contact_center__area_name', 'contact_center').annotate(
            scheduled_time_sum=Sum('scheduled_time'),
            ready_sum=Sum('ready'),
            rating_avg=Avg('rating'),
            adherence_avg=Avg('adherence'),
            sick_leave_sum=Sum('sick_leave'),
            absenteeism_sum=Sum('absenteeism'))
    else:
        date = ReportData.objects.order_by('-date').values('date').first()
        date = date['date'].strftime('%Y')
        data = ReportData.objects.filter(contact_center=pk, date__year=date, job__calculated=True).values(
            'date',
            'contact_center__area_name', 'contact_center').annotate(
            scheduled_time_sum=Sum('scheduled_time'),
            ready_sum=Sum('ready'),
            rating_avg=Avg('rating'),
            adherence_avg=Avg('adherence'),
            sick_leave_sum=Sum('sick_leave'),
            absenteeism_sum=Sum('absenteeism'))
    return data


def group_detail_service(pk: int, start_date: str = None, end_date: str = None):
    if start_date and end_date:
        data = ReportData.objects.filter(group=pk,
                                         date__range=[start_date, end_date],
                                         job__calculated=True).values('date',
                                                                      'group__group_name',
                                                                      'group').annotate(
            scheduled_time_sum=Sum('scheduled_time'),
            ready_sum=Sum('ready'),
            rating_avg=Avg('rating'),
            adherence_avg=Avg('adherence'),
            sick_leave_sum=Sum('sick_leave'),
            absenteeism_sum=Sum('absenteeism'))
    else:
        date = ReportData.objects.order_by('-date').values('date').first()
        date = date['date'].strftime('%Y')
        data = ReportData.objects.filter(group=pk,
                                         date__year=date, job__calculated=True).values('date',
                                                                                       'group__group_name',
                                                                                       'group').annotate(
            scheduled_time_sum=Sum('scheduled_time'),
            ready_sum=Sum('ready'),
            rating_avg=Avg('rating'),
            adherence_avg=Avg('adherence'),
            sick_leave_sum=Sum('sick_leave'),
            absenteeism_sum=Sum('absenteeism'))
    return data


def employee_detail_service(name: str, start_date: str = None, end_date: str = None):
    if start_date and end_date:
        data = ReportData.objects.filter(full_name=name,
                                         date__range=[start_date, end_date],
                                         ).values('date').annotate(
            scheduled_time_sum=Sum('scheduled_time'),
            ready_sum=Sum('ready'),
            rating_avg=Avg('rating'),
            adherence_avg=Avg('adherence'),
            sick_leave_sum=Sum('sick_leave'),
            absenteeism_sum=Sum('absenteeism'))
    else:
        date = ReportData.objects.order_by('-date').values('date').first()
        date = date['date'].strftime('%Y')
        data = ReportData.objects.filter(full_name=name,
                                         date__year=date, ).values('date').annotate(
            scheduled_time_sum=Sum('scheduled_time'),
            ready_sum=Sum('ready'),
            rating_avg=Avg('rating'),
            adherence_avg=Avg('adherence'),
            sick_leave_sum=Sum('sick_leave'),
            absenteeism_sum=Sum('absenteeism'))
    return data


def dates_parse(request, start_date: str = None, end_date: str = None):
    try:
        start_date_check = datetime.strptime(request.POST.get('start_date'), '%Y-%m-%d')
        end_date_check = datetime.strptime(request.POST.get('end_date'), '%Y-%m-%d')
        if end_date_check >= start_date_check:
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')
        else:
            messages.add_message(request, messages.WARNING,
                                 mark_safe("Конечная дата не может быть меньше начальной"))
    except:
        messages.add_message(request, messages.WARNING, mark_safe("Выберите дату начала и дату конца периода"))
    return start_date, end_date


def rating_leaders(leaders: dict) -> list:
    res = []
    for leader in leaders:
        if len(res) < 10:
            res.append(leader)
        else:
            if res[-1]['rating'] == leader['rating']:
                res.append(leader)
            else:
                break
    return res
