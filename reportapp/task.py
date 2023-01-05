import csv
import datetime
from typing import Union

from reportapp.models import Area, Group, JobTitle, ReportData
from config.settings import MEDIA_ROOT

YEAR_START_SERVICE = 2022
FIRST_MONTH_DAY = '01'
MONTH_DICT = {
    'январь': '01',
    'февраль': '02',
    'март': '03',
    'апрель': '04',
    'май': '05',
    'июнь': '06',
    'июль': '07',
    'август': '08',
    'сентябрь': '09',
    'октябрь': '10',
    'ноябрь': '11',
    'декабрь': '12'
}
GROUP_LIST = list(Group.objects.values_list('group_name', flat=True))
UCC_LIST = list(Area.objects.values_list('area_name', flat=True))
POSITION_LIST = list(JobTitle.objects.values_list('position', flat=True))
SPECIAL_CHAR_FOR_SPACE = '\xa0%'
ERR_MESSAGE = 'Ошибка'


def insert_data(file_name: str):
    file = open_file(file_name)
    if isinstance(file, list):
        for f in file:
            report_data = ReportData()
            report_data.date = f['date']
            report_data.full_name = f['full_name']
            report_data.group = Group.objects.filter(group_name=f['group']).first()
            report_data.job = JobTitle.objects.filter(position=f['job']).first()
            report_data.contact_center = Area.objects.filter(area_name=f['contact_center']).first()
            report_data.scheduled_time = f['scheduled_time']
            report_data.ready = f['ready']
            report_data.adherence = f['adherence']
            report_data.sick_leave = f['sick_leave']
            report_data.absenteeism = f['absenteeism']
            report_data.rating = f['rating']
            report_data.save()
    else:
        print(file)


def open_file(file_name: str):
    res = []
    with open(MEDIA_ROOT / file_name, 'r', newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=';')
        next(csvfile)
        idx = 2
        for row in reader:
            if len(row) != 10:
                return f'В строке {idx} ошибка. Не хватает данных'
            data = validation(row)
            if isinstance(data, dict):
                # Механизм расчета рейтинга пока тестовый
                if data['absenteeism'] > 10:
                    data['rating'] = 0
                else:
                    data['rating'] = (data['ready'] / data['scheduled_time']) * data['adherence']
                res.append(data)
                idx += 1
            else:
                return f'В строке {idx} {ERR_MESSAGE}'
    return res


def validation(file_row: list):
    result = {
        'full_name': file_row[0].strip(),
        'group': valid_lists(file_row[1], GROUP_LIST),
        'date': data_valid_create(file_row[2]),
        'job': valid_lists(file_row[3], POSITION_LIST),
        'contact_center': valid_lists(file_row[4], UCC_LIST),
        'absenteeism': numeric_valid(file_row[5]),
        'scheduled_time': numeric_valid(file_row[6]),
        'ready': numeric_valid(file_row[7]),
        'sick_leave': numeric_valid(file_row[8]),
        'adherence': numeric_valid(file_row[9])
    }
    if ERR_MESSAGE not in result.values():
        return result
    else:
        return ERR_MESSAGE


def valid_lists(title: str, group: list) -> str:
    if title in group:
        return title
    else:
        print(f'Ошибка в проверке списка {group} пришло значение {title}')
        return ERR_MESSAGE


# ToDo: Не забудь поправить формат даты на Excel
def data_valid_create(year: str) -> str:
    curr_year = datetime.datetime.now().year
    try:
        date = datetime.datetime.strptime(year, '%m/%d/%y')
        if YEAR_START_SERVICE <= date.year <= curr_year:
            result = str(date.year) + '-' + str(date.month) + '-' + FIRST_MONTH_DAY
            return result
        else:
            print(f'Ошибка в дате {date}')
            return ERR_MESSAGE
    except ValueError:
        print(f'Ошибка в формате данных {year}')
        return ERR_MESSAGE


def numeric_valid(num: str, sign: str = None):
    if sign is not None:
        if num.count(',') <= 1 and num.count(sign) == 1:
            inter_res = num.replace(sign, '').split(',')
        else:
            return ERR_MESSAGE
    else:
        if num.count(',') <= 1:
            inter_res = num.split(',')
        else:
            print('Ошибка в числе на разбивке по запятой')
            return ERR_MESSAGE
    if len(inter_res) == 1 and inter_res[0].isdigit():
        res = float(inter_res[0])
    elif inter_res[0].isdigit() and inter_res[1].isdigit():
        res = float('.'.join(inter_res))
    else:
        print('Ошибка 1')
        return ERR_MESSAGE
    if sign is not None:
        return res / 100
    else:
        return res
