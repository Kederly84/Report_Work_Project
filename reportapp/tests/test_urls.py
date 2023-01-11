from django.test import SimpleTestCase
from django.urls import reverse, resolve
from reportapp.views import upload, ContactCenterView, ContactCenterDetailView, GroupView, GroupDetailView, \
    EmployeeView, EmployeeDetailView, RatingLeaders


class TestUrls(SimpleTestCase):

    def test_upload_url_is_resolved(self):
        url = reverse('report:upload')
        self.assertEquals(resolve(url).func, upload)

    def test_home_url_is_resolved(self):
        url = reverse('report:home')
        self.assertEquals(resolve(url).func.view_class, ContactCenterView)

    def test_center_detail_url_is_resolved(self):
        url = reverse('report:center_detail', args=[1])
        self.assertEquals(resolve(url).func.view_class, ContactCenterDetailView)

    def test_group_url_is_resolved(self):
        url = reverse('report:group', args=[1])
        self.assertEquals(resolve(url).func.view_class, GroupView)

    def test_group_detail_url_is_resolved(self):
        url = reverse('report:group_detail', args=[1])
        self.assertEquals(resolve(url).func.view_class, GroupDetailView)

    def test_employee_url_is_resolved(self):
        url = reverse('report:employee', args=[1])
        self.assertEquals(resolve(url).func.view_class, EmployeeView)

    def test_employee_detail_url_is_resolved(self):
        url = reverse('report:employee_detail', args=['some name'])
        self.assertEquals(resolve(url).func.view_class, EmployeeDetailView)

    def test_leaders_url_is_resolved(self):
        url = reverse('report:leaders')
        self.assertEquals(resolve(url).func.view_class, RatingLeaders)

