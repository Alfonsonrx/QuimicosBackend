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


class UserCreateAndPromotionTests(APITestCase):
  def setUp(self):
    self.admin = User.objects.create_user('admin@x.com', 'Ana', 'Admin', 'AdminPass123!', type=User.UserType.ADMIN)
    self.client.force_authenticate(self.admin)
    self.payload = {'email': 'new@x.com', 'password': 'NewPass123!', 're_password': 'NewPass123!',
                    'name': 'Nuevo', 'first_lastname': 'Usuario'}

  def test_create_employee_returns_user(self):
    r = self.client.post('/accounts_api/registration/', self.payload)
    self.assertEqual(r.status_code, 201)
    self.assertEqual(r.data['type'], 'empleado')
    self.assertEqual(r.data['email'], 'new@x.com')
    self.assertIn('id', r.data)
    self.assertNotIn('password', r.data)
    self.assertNotIn('admin_password', r.data)

  def test_create_admin_requires_password(self):
    data = {**self.payload, 'type': 'administrador'}
    self.assertEqual(self.client.post('/accounts_api/registration/', data).status_code, 403)
    self.assertEqual(self.client.post('/accounts_api/registration/', {**data, 'admin_password': 'wrong'}).status_code, 403)
    self.assertFalse(User.objects.filter(email='new@x.com').exists())

    r = self.client.post('/accounts_api/registration/', {**data, 'admin_password': 'AdminPass123!'})
    self.assertEqual(r.status_code, 201)
    self.assertEqual(r.data['type'], 'administrador')

  def test_promote_requires_password(self):
    emp = User.objects.create_user('emp@x.com', 'Eva', 'Emp', 'pass')
    url = f'/accounts_api/users/{emp.id}/'
    self.assertEqual(self.client.patch(url, {'type': 'administrador'}).status_code, 403)
    r = self.client.patch(url, {'type': 'administrador', 'admin_password': 'AdminPass123!'})
    self.assertEqual(r.status_code, 200)
    # Already admin: editing other fields needs no password
    self.assertEqual(self.client.patch(url, {'phone': '123'}).status_code, 200)
