import csv
import datetime
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
            report_data.date = f[0]
            report_data.full_name = f[1]
            report_data.group = Group.objects.filter(group_name=f[2]).first()
            report_data.job = JobTitle.objects.filter(position=f[3]).first()
            report_data.contact_center = Area.objects.filter(area_name=f[4]).first()
            report_data.scheduled_time = f[5]
            report_data.ready = f[6]
            report_data.share_ready = f[7]
            report_data.adherence = f[8]
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
            if isinstance(data, list):
                res.append(data)
                idx += 1
            else:
                return f'В строке {idx} {ERR_MESSAGE}'
    return res


def validation(file_row: list) -> list | str:
    result = [
        data_valid_create(file_row[0], file_row[1]),
        file_row[2],
        valid_lists(file_row[3], GROUP_LIST),
        valid_lists(file_row[4], POSITION_LIST),
        valid_lists(file_row[5], UCC_LIST),
        numeric_valid(file_row[6]),
        numeric_valid(file_row[7]),
        numeric_valid(file_row[8], SPECIAL_CHAR_FOR_SPACE),
        numeric_valid(file_row[9], SPECIAL_CHAR_FOR_SPACE)
    ]
    if ERR_MESSAGE not in result:
        return result
    else:
        return ERR_MESSAGE


def valid_lists(title: str, group: list) -> str:
    if title in group:
        return title
    else:
        return ERR_MESSAGE


def data_valid_create(year: str, month: str) -> str:
    curr_year = datetime.datetime.now().year
    if not year.isdigit() and not YEAR_START_SERVICE <= int(year) <= curr_year:
        return ERR_MESSAGE
    if not month.strip().isalpha() and not month.strip().lower() in MONTH_DICT.keys():
        return ERR_MESSAGE
    date = year.strip()+'-'+MONTH_DICT[month.strip()]+'-'+FIRST_MONTH_DAY
    return date


def numeric_valid(num: str, sign: str = None) -> float | str:
    if sign is not None:
        if num.count(',') <= 1 and num.count(sign) == 1:
            inter_res = num.replace(sign, '').split(',')
        else:
            return ERR_MESSAGE
    else:
        if num.count(',') <= 1:
            inter_res = num.split(',')
        else:
            return ERR_MESSAGE
    if len(inter_res) == 1 and inter_res[0].isdigit():
        res = float(inter_res[0])
    elif inter_res[0].isdigit() and inter_res[1].isdigit():
        res = float('.'.join(inter_res))
    else:
        return ERR_MESSAGE
    if sign is not None:
        return res / 100
    else:
        return res
