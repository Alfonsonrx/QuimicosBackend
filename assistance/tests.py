from datetime import date, time

from django.utils import timezone
from rest_framework.test import APITestCase

from accounts.models import User
from assistance.models import AssistanceRecord, WorkSchedule

URL = '/assistance_api/assistances/'


class AssistanceMarkingTests(APITestCase):
  def setUp(self):
    self.admin = User.objects.create_user('admin@x.com', 'Ana', 'Admin', 'pass', type=User.UserType.ADMIN)
    self.emp = User.objects.create_user('emp@x.com', 'Eva', 'Emp', 'pass', second_lastname='Soto', position='Bodega')
    self.today = timezone.localdate()

  def mark(self, type_, hhmm, day=None, as_user=None):
    self.client.force_authenticate(as_user or self.emp)
    h, m = hhmm
    return self.client.post(URL, {'user': self.emp.id, 'type': type_, 'date': day or self.today, 'time': time(h, m)})

  def test_name_position_and_thresholds(self):
    r = self.mark('ingreso', (9, 30))
    self.assertEqual(r.status_code, 201)
    self.assertEqual(r.data['name'], 'Eva Emp Soto')
    self.assertEqual(r.data['position'], 'Bodega')
    self.assertFalse(r.data['delay'])
    self.assertTrue(self.mark('ingreso', (9, 31), day=date(2026, 1, 5)).data['delay'])
    self.assertFalse(self.mark('salida', (17, 30)).data['early_exit'])
    self.assertTrue(self.mark('salida', (17, 29), day=date(2026, 1, 5)).data['early_exit'])

  def test_schedule_change_only_affects_new_marks(self):
    old = self.mark('ingreso', (9, 15)).data
    self.client.force_authenticate(self.emp)
    self.assertEqual(self.client.patch('/assistance_api/schedule/', {'entry_time': '09:00'}).status_code, 403)
    self.client.force_authenticate(self.admin)
    self.assertEqual(self.client.patch('/assistance_api/schedule/', {'entry_time': '18:00'}).status_code, 400)
    self.assertEqual(self.client.patch('/assistance_api/schedule/', {'entry_time': '09:00'}).status_code, 200)
    self.assertTrue(self.mark('ingreso', (9, 15), day=date(2026, 1, 5)).data['delay'])
    self.assertFalse(AssistanceRecord.objects.get(pk=old['id']).delay)

  def test_no_double_marks(self):
    self.assertEqual(self.mark('salida', (8, 0)).status_code, 400)
    self.assertEqual(self.mark('ingreso', (9, 0)).status_code, 201)
    self.assertEqual(self.mark('ingreso', (9, 5)).status_code, 400)
    self.assertEqual(self.mark('salida', (18, 0)).status_code, 201)
    self.assertEqual(self.mark('salida', (18, 5)).status_code, 400)
    self.assertEqual(self.mark('ingreso', (9, 0), day=date(2026, 1, 5)).status_code, 201)

  def test_reentry_with_permit(self):
    status_url = URL + 'today-status/'
    self.client.force_authenticate(self.emp)
    self.assertEqual(self.client.get(status_url).data['next'], 'ingreso')
    self.mark('ingreso', (9, 0))
    self.assertEqual(self.client.get(status_url).data['next'], 'salida')

    self.client.force_authenticate(self.admin)
    self.assertEqual(self.client.post(URL + 'allow-reentry/', {'user': self.emp.id}).status_code, 400)  # no salida yet

    self.assertTrue(self.mark('salida', (13, 0)).data['early_exit'])
    self.client.force_authenticate(self.emp)
    self.assertIsNone(self.client.get(status_url).data['next'])
    self.assertEqual(self.mark('ingreso', (14, 0)).status_code, 400)
    self.assertEqual(self.client.post(URL + 'allow-reentry/', {'user': self.emp.id}).status_code, 403)

    self.client.force_authenticate(self.admin)
    self.assertEqual(self.client.post(URL + 'allow-reentry/', {'user': self.emp.id}).status_code, 201)
    self.client.force_authenticate(self.emp)
    self.assertEqual(self.client.get(status_url).data['next'], 'ingreso')
    r = self.mark('ingreso', (14, 0))
    self.assertEqual(r.status_code, 201)
    self.assertFalse(r.data['delay'])  # only the day's first ingreso can be late
    self.assertEqual(self.mark('salida', (18, 0)).status_code, 201)
    self.assertEqual(self.mark('ingreso', (18, 30)).status_code, 400)  # permit was single-use

    s = self.client.get(status_url).data
    self.assertEqual((s['ingreso'], s['salida'], s['next'], len(s['records'])), (time(9, 0), time(18, 0), None, 4))

  def test_admin_patch_recomputes_flags(self):
    rec = self.mark('ingreso', (9, 0)).data
    self.client.force_authenticate(self.admin)
    r = self.client.patch(f"{URL}{rec['id']}/", {'time': '10:00'})
    self.assertTrue(r.data['delay'])
    self.assertEqual(WorkSchedule.get().entry_time, time(9, 30))
