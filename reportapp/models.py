from authapp.models import NULLABLE
from django.db import models


class BaseModel(models.Model):
    created = models.DateTimeField(auto_now_add=True, verbose_name='Создано')
    updated = models.DateTimeField(auto_now_add=True, verbose_name='Обновлено')
    deleted = models.BooleanField(default=False, verbose_name='Удалено')

    class Meta:
        abstract = True

    def delete(self, *args, **kwargs):
        self.deleted = True
        self.save()


class Area(BaseModel):
    area_name = models.CharField(max_length=100, verbose_name='Название площадки', unique=True)

    class Meta:
        verbose_name = 'Площадка'
        verbose_name_plural = 'Площадки'
        ordering = ['area_name']

    def __str__(self):
        return f'{self.area_name}'


class Group(BaseModel):
    group_name = models.CharField(max_length=100, verbose_name='Название группы', unique=True)

    class Meta:
        verbose_name = 'Группа опереторов'
        verbose_name_plural = 'Группы операторов'
        ordering = ['group_name']

    def __str__(self):
        return f'{self.group_name}'


class JobTitle(BaseModel):
    position = models.CharField(max_length=100, verbose_name='Должность', unique=True)

    class Meta:
        verbose_name = 'Должность'
        verbose_name_plural = 'Должности'
        ordering = ['position']

    def __str__(self):
        return f'{self.position}'


class ReportData(BaseModel):
    date = models.DateField(auto_now=False, verbose_name='Дата', **NULLABLE)
    full_name = models.CharField(max_length=255, verbose_name='ФИО')
    group = models.ForeignKey(Group, on_delete=models.PROTECT, verbose_name='Группа')
    job = models.ForeignKey(JobTitle, on_delete=models.PROTECT, verbose_name='Должность')
    contact_center = models.ForeignKey(Area, on_delete=models.PROTECT, verbose_name='Площадка',
                                       related_name='contact_center')
    scheduled_time = models.FloatField(verbose_name='запланированное время')
    ready = models.FloatField(verbose_name='Ready')
    adherence = models.FloatField(verbose_name='Соблюдение расписания')
    sick_leave = models.FloatField(default=0, verbose_name='Больничные')
    absenteeism = models.FloatField(default=0, verbose_name='Отсутсвия')
    rating = models.FloatField(default=0, verbose_name='Рейтинг')

    class Meta:
        verbose_name = 'Данные отчета'
        verbose_name_plural = 'Данные отчета'
        ordering = ['date', 'contact_center', 'group', 'full_name', 'rating']
