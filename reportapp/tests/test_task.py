from reportapp.tests.test_views import BaseTestClass
from reportapp.task import valid_lists, data_valid_create, numeric_valid, ERR_MESSAGE
from reportapp.models import Area, Group, ReportData
from datetime import datetime


class TaskTest(BaseTestClass):

    def setUp(self) -> None:
        super().setUp()

    def test_valid_list_right_data(self):
        unit = Area.objects.first().area_name
        units = list(Area.objects.values_list('area_name', flat=True))
        result = valid_lists(unit, units)
        self.assertEqual(result, unit)

    def test_valid_list_wrong_data(self):
        unit = 'Some wrong unit'
        units = list(Group.objects.values_list('group_name', flat=True))
        result = valid_lists(unit, units)
        self.assertEqual(result, ERR_MESSAGE)

    def test_data_valid_create_right_date(self):
        date = ReportData.objects.first().date
        date_check = datetime.strftime(date, '%Y-%m-%d')
        date_for_func = datetime.strftime(date, '%m/%d/%y')
        result = data_valid_create(date_for_func)
        self.assertEqual(result, date_check)

    def test_data_valid_create_wrong_date(self):
        date_for_func = '1/12/25'
        result = data_valid_create(date_for_func)
        self.assertEqual(result, ERR_MESSAGE)

    def test_numeric_valid_right_data(self):
        data = '25,25'
        result = numeric_valid(data)
        self.assertEqual(result, 25.25)

    def test_numeric_valid_wrong_data(self):
        data = '25,25,25'
        result = numeric_valid(data)
        self.assertEqual(result, ERR_MESSAGE)

