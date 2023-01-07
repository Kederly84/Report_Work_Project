from django.contrib import admin
from django.utils.html import format_html

from reportapp.models import Area, Group, JobTitle, ReportData
from rangefilter.filters import DateRangeFilter, NumericRangeFilter


@admin.register(ReportData)
class ReportDataAdmin(admin.ModelAdmin):
    list_display = ('date', 'slug', 'group', 'job', 'contact_center', 'sick_leave', 'absenteeism')
    list_per_page = 20
    list_filter = (
        ('created', DateRangeFilter), ('date', DateRangeFilter), ('rating', NumericRangeFilter), 'group', 'job',
        'contact_center')
    search_fields = ('full_name',)
    date_hierarchy = 'created'
    show_full_result_count = False

    def slug(self, obj):
        return format_html(
            '<a href="http://127.0.0.1:8000/admin/reportapp/reportdata/{}/change/">{}</a>',
            obj.pk,
            obj.full_name
        )


@admin.register(Area)
class AdminArea(admin.ModelAdmin):
    list_display = ('area_name', 'pk')
    list_per_page = 20
    search_fields = ('area_name',)


@admin.register(Group)
class AdminGroup(admin.ModelAdmin):
    list_display = ('group_name', 'pk')
    list_per_page = 20
    search_fields = ('group_name',)


@admin.register(JobTitle)
class AdminJobTitle(admin.ModelAdmin):
    list_display = ('position', 'calculated')
    list_per_page = 20
    search_fields = ('position', 'calculated')
