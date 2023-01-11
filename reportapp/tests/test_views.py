from http import HTTPStatus
from django.test import TestCase, Client
from django.urls import reverse, resolve
from reportapp.models import Area, Group, JobTitle, ReportData
from django.contrib.messages import get_messages


class BaseTestClass(TestCase):

    def setUp(self) -> None:
        Area.objects.create(area_name=f'Area {1}')
        Group.objects.create(group_name=f'Group {1}')
        JobTitle.objects.create(position=f'Job Title {1}')
        for i in range(15):
            ReportData.objects.create(
                date='2022-10-1',
                full_name=f'Name {i}',
                group=Group.objects.all().first(),
                job=JobTitle.objects.all().first(),
                contact_center=Area.objects.all().first(),
                scheduled_time=100 + i * 10,
                ready=80 + i * 10,
                adherence=0.8 + i / 100,
                rating=i
            )

    @staticmethod
    def data_for_test(unit: str = None, pk: int = None, name: str = None):
        if pk and unit == 'contact_center':
            data = ReportData.objects.filter(contact_center=pk, job__calculated=True)
        elif pk and unit == 'group':
            data = ReportData.objects.filter(group=pk, job__calculated=True)
        elif pk and unit == 'employee':
            data = ReportData.objects.filter(group=pk, job__calculated=True)
            sch_time = data.first().scheduled_time
            ready = data.first().ready
            adh = data.first().adherence
            return sch_time, ready, adh
        elif not pk and unit == 'employee' and name:
            data = ReportData.objects.filter(full_name=name)
            sch_time = data.first().scheduled_time
            ready = data.first().ready
            adh = data.first().adherence
            return sch_time, ready, adh
        else:
            data = ReportData.objects.filter(job__calculated=True)
        sch_time = 0
        ready = 0
        adh = 0
        for obj in data:
            sch_time += obj.scheduled_time
            ready += obj.ready
            adh += obj.adherence
        adh /= len(data)
        return sch_time, ready, adh


class BaseViewTest(object):

    def test_status(self):
        result = self.client.get(self.url)
        self.assertEqual(result.status_code, HTTPStatus.OK)

    def test_template(self):
        result = self.client.get(self.url)
        self.assertTemplateUsed(result, 'reportapp/report.html')

    def test_context(self):
        response = self.client.get(self.url)
        self.assertEqual(response.context['data'][0]['ready_sum'], round(self.ready, 2))
        self.assertEqual(response.context['data'][0]['scheduled_time_sum'], round(self.sch_time, 2))
        self.assertEqual(response.context['data'][0]['adherence_avg'], round(self.adh, 2))


class BaseDetailViewTest(object):

    def check_for_test(self, response, messages=None):
        if messages:
            self.assertEqual(str(messages[0]), "Выберите дату начала и дату конца периода")
        self.assertEqual(response.context['data'][0]['ready_sum'], round(self.ready, 2))
        self.assertEqual(response.context['data'][0]['scheduled_time_sum'], round(self.sch_time, 2))
        self.assertEqual(response.context['data'][0]['adherence_avg'], round(self.adh, 2))

    def test_status(self):
        result = self.client.get(self.url)
        self.assertEqual(result.status_code, HTTPStatus.OK)

    def test_template(self):
        result = self.client.get(self.url)
        self.assertTemplateUsed(result, 'reportapp/report.html')

    def test_get_method(self):
        response = self.client.get(self.url)
        self.check_for_test(response)

    def test_correct_post_method(self):
        response = self.client.post(self.url, {'start_date': '2022-10-1', 'end_date': '2022-10-1'})
        self.check_for_test(response)

    def test_start_date_post(self):
        response = self.client.post(self.url, {'start_date': '2022-10-1', 'end_date': 'End date'})
        messages = list(get_messages(response.wsgi_request))
        self.check_for_test(response, messages)

    def test_end_date_post(self):
        response = self.client.post(self.url, {'start_date': 'Start date', 'end_date': '2022-10-1'})
        messages = list(get_messages(response.wsgi_request))
        self.check_for_test(response, messages)

    def test_without_date_post(self):
        response = self.client.post(self.url, {'start_date': 'Start date', 'end_date': 'End date'})
        messages = list(get_messages(response.wsgi_request))
        self.check_for_test(response, messages)


class ContactCenterTestView(BaseTestClass, BaseViewTest):

    def setUp(self) -> None:
        super().setUp()
        self.url = reverse('report:home')
        self.unit = 'contact_center'
        self.sch_time, self.ready, self.adh = self.data_for_test(self.unit)


class ContactCenterDetailTestView(BaseTestClass, BaseDetailViewTest):

    def setUp(self) -> None:
        super().setUp()
        self.contact_center = Area.objects.first().pk
        self.url = reverse('report:center_detail', args=[self.contact_center])
        self.unit = 'contact_center'
        self.sch_time, self.ready, self.adh = self.data_for_test(self.unit, self.contact_center)


class GroupTestView(BaseTestClass, BaseViewTest):

    def setUp(self) -> None:
        super().setUp()
        self.group = Group.objects.first().pk
        self.url = reverse('report:group', args=[self.group])
        self.unit = 'group'
        self.sch_time, self.ready, self.adh = self.data_for_test(self.unit, self.group)


class GroupDetailTestView(BaseTestClass, BaseDetailViewTest):

    def setUp(self) -> None:
        super().setUp()
        self.group = Group.objects.first().pk
        self.url = reverse('report:group_detail', args=[self.group])
        self.unit = 'group'
        self.sch_time, self.ready, self.adh = self.data_for_test(self.unit, self.group)


class EmployeeTestView(BaseTestClass, BaseViewTest):

    def setUp(self) -> None:
        super().setUp()
        self.group = Group.objects.first().pk
        self.url = reverse('report:employee', args=[self.group])
        self.unit = 'employee'
        self.sch_time, self.ready, self.adh = self.data_for_test(self.unit, self.group)


class EmployeeDetailTestView(BaseTestClass, BaseDetailViewTest):

    def setUp(self) -> None:
        super().setUp()
        self.name = ReportData.objects.first().full_name
        self.url = reverse('report:employee_detail', args=[self.name])
        self.unit = 'employee'
        self.sch_time, self.ready, self.adh = self.data_for_test(self.unit, name=self.name)


class RatingLeadersTestView(BaseTestClass):

    def setUp(self) -> None:
        super().setUp()
        self.leaders = ReportData.objects.all().order_by('-rating')[:10]
        self.url = reverse('report:leaders')
        self.unit = 'leaders'
        self.check = {
            'full_name': self.leaders[0].full_name,
            'rating': self.leaders[0].rating,
            'date': self.leaders[0].date,
        }

    def test_response_status(self):
        result = self.client.get(self.url)
        self.assertEqual(result.status_code, HTTPStatus.OK)

    def test_template_name(self):
        result = self.client.get(self.url)
        self.assertTemplateUsed(result, 'reportapp/leaders.html')

    def test_context_length(self):
        result = self.client.get(self.url)
        self.assertEqual(len(result.context['data']), len(self.leaders))

    def test_get_context(self):
        result = self.client.get(self.url)
        self.assertEqual(result.context['data'][0], self.check)

    def test_post_correct_date(self):
        result = self.client.post(self.url, {'leaders_date': '2022-10-1'})
        self.assertEqual(result.context['data'][0], self.check)
        self.assertEqual(len(result.context['data']), len(self.leaders))

    def test_post_without_date(self):
        result = self.client.post(self.url, {'leaders_date': 'Выберите дату'})
        messages = list(get_messages(result.wsgi_request))
        self.assertEqual(str(messages[0]), "Выберите дату")
        self.assertEqual(result.context['data'][0], self.check)
        self.assertEqual(len(result.context['data']), len(self.leaders))

    def test_post_incorrect_date(self):
        result = self.client.post(self.url, {'leaders_date': '2022-11-1'})
        self.assertEqual(len(result.context['data']), 0)
