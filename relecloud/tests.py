
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.core import mail
from .models import Cruise, InfoRequest
from django.utils import timezone

@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class InfoRequestFormTests(TestCase):
	def setUp(self):
		self.client = Client()
		self.cruise = Cruise.objects.create(
			name="Test Cruise",
			description="Test description",
			departure_date=timezone.now().date()
		)
		self.url = reverse('info_request')

	def test_info_request_success(self):
		data = {
			'name': 'Miguel',
			'email': 'miguel@example.com',
			'cruise': self.cruise.id,
			'notes': 'Quiero información',
		}
		response = self.client.post(self.url, data, follow=True)
		self.assertContains(response, '¡Solicitud enviada correctamente!')
		self.assertEqual(InfoRequest.objects.count(), 1)
		self.assertEqual(len(mail.outbox), 1)
		self.assertIn('Miguel', mail.outbox[0].body)
		self.assertIn('Test Cruise', mail.outbox[0].body)

	def test_info_request_duplicate(self):
		InfoRequest.objects.create(
			name='Miguel',
			email='miguel@example.com',
			cruise=self.cruise,
			notes='Primera solicitud',
		)
		data = {
			'name': 'Miguel',
			'email': 'miguel@example.com',
			'cruise': self.cruise.id,
			'notes': 'Segunda solicitud',
		}
		response = self.client.post(self.url, data, follow=True)
		self.assertContains(response, 'Ya has enviado una solicitud para este crucero')
		self.assertEqual(InfoRequest.objects.count(), 1)
		self.assertEqual(len(mail.outbox), 0)
