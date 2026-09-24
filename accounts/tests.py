from datetime import date, time

from rest_framework.test import APITestCase

from accounts.models import User
from assistance.models import AssistanceRecord


class UserCrudTests(APITestCase):
  def setUp(self):
    self.admin = User.objects.create_user('admin@x.com', 'Ana', 'Admin', 'pass', type=User.UserType.ADMIN)
    self.emp = User.objects.create_user('emp@x.com', 'Eva', 'Emp', 'pass')
    AssistanceRecord.objects.create(user=self.emp, date=date.today(), time=time(9, 0))

  def test_admin_crud(self):
    self.client.force_authenticate(self.admin)
    self.assertEqual(self.client.get('/accounts_api/users/').data['count'], 2)
    self.assertEqual(self.client.get(f'/accounts_api/users/{self.emp.id}/').data['email'], 'emp@x.com')

    r = self.client.patch(f'/accounts_api/users/{self.emp.id}/', {'phone': '123'})
    self.assertEqual(r.status_code, 200)
    self.assertEqual(r.data['phone'], '123')

    self.assertEqual(self.client.delete(f'/accounts_api/users/{self.emp.id}/').status_code, 204)
    self.emp.refresh_from_db()
    self.assertFalse(self.emp.is_active)
    self.assertEqual(self.emp.assistances.count(), 1)

  def test_employee(self):
    self.client.force_authenticate(self.emp)
    self.assertEqual(self.client.get('/accounts_api/users/').status_code, 403)
    self.assertEqual(self.client.patch(f'/accounts_api/users/{self.emp.id}/', {'type': 'administrador'}).status_code, 403)
    r = self.client.get('/accounts_api/users/me/')
    self.assertEqual(r.status_code, 200)
    self.assertEqual(r.data['id'], self.emp.id)

  def test_anonymous_me(self):
    self.assertEqual(self.client.get('/accounts_api/users/me/').status_code, 401)
