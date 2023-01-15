from django.contrib.messages import get_messages
from django.contrib.messages.storage.fallback import FallbackStorage
from django.http import HttpRequest
from django.test import TestCase

from reportapp.models import Area, Group, ReportData
from reportapp.services.report_services import contact_center_detail_service, group_detail_service, \
    employee_detail_service, dates_parse
from reportapp.tests.test_views import BaseTestClass


class ContactCenterDetailServiceTest(BaseTestClass):

    def setUp(self) -> None:
        super().setUp()
        self.unit_pk = Area.objects.first().pk
        self.unit = 'contact_center'
        self.sch_time, self.ready, self.adh = self.data_for_test(self.unit, self.unit_pk)
        self.func = contact_center_detail_service

    def check_result(self, result_for_check):
        self.assertEqual(result_for_check[0]['ready_sum'], round(self.ready, 2))
        self.assertEqual(result_for_check[0]['scheduled_time_sum'], round(self.sch_time, 2))
        self.assertEqual(result_for_check[0]['adherence_avg'], round(self.adh, 2))

    def test_without_date(self):
        result_for_check = self.func(self.unit_pk)
        self.check_result(result_for_check)

    def test_with_start_date(self):
        result_for_check = self.func(self.unit_pk, start_date='2022-10-1')
        self.check_result(result_for_check)

    def test_with_end_date(self):
        result_for_check = self.func(self.unit_pk, end_date='2022-10-1')
        self.check_result(result_for_check)

    def test_with_dates(self):
        result_for_check = self.func(self.unit_pk, start_date='2022-10-1', end_date='2022-10-1')
        self.check_result(result_for_check)


class GrouDetailServiceTest(ContactCenterDetailServiceTest):

    def setUp(self) -> None:
        super().setUp()
        self.unit_pk = Group.objects.first().pk
        self.unit = 'group'
        self.func = group_detail_service


class EmployeeDetailServiceTest(ContactCenterDetailServiceTest):

    def setUp(self) -> None:
        super().setUp()
        self.unit_pk = ReportData.objects.first().full_name
        self.unit = 'employee'
        self.func = employee_detail_service
        self.sch_time, self.ready, self.adh = self.data_for_test(self.unit, name=self.unit_pk)


class DataParseTest(TestCase):

    def setUp(self) -> None:
        self.request = HttpRequest()
        self.request.method = 'POST'
        setattr(self.request, 'session', 'session')
        messages = FallbackStorage(self.request)
        setattr(self.request, '_messages', messages)
        self.first_date = '2021-10-01'
        self.second_date = '2021-11-01'

    def test_correct_data(self):
        self.request.POST['start_date'] = self.first_date
        self.request.POST['end_date'] = self.second_date
        start_date, end_date = dates_parse(self.request)
        self.assertEqual(start_date, self.first_date)
        self.assertEqual(end_date, self.second_date)

    def test_incorrect_date(self):
        self.request.POST['start_date'] = self.second_date
        self.request.POST['end_date'] = self.first_date
        dates_parse(self.request)
        messages = list(get_messages(self.request))
        self.assertEqual(str(messages[0]), 'Конечная дата не может быть меньше начальной')

    def test_with_only_start_date(self):
        self.request.POST['start_date'] = self.first_date
        dates_parse(self.request)
        messages = list(get_messages(self.request))
        self.assertEqual(str(messages[0]), 'Выберите дату начала и дату конца периода')

    def test_with_only_end_date(self):
        self.request.POST['end_date'] = self.second_date
        dates_parse(self.request)
        messages = list(get_messages(self.request))
        self.assertEqual(str(messages[0]), 'Выберите дату начала и дату конца периода')
