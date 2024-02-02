from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from .models import Message


class MessageAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_create_message(self):
        data = {'text': 'Hello, World!'}
        response = self.client.post('/api/messages/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Message.objects.count(), 1)
        self.assertEqual(Message.objects.get().text, 'Hello, World!')


class WebhookReceiverViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.message = Message.objects.create(text='Test', timestamp='2022-01-01T00:00:00Z')

    def test_webhook_receiver_view(self):
        url = reverse('webhook-receiver')
        data_from_consumer = {'message_id': self.message.id, 'result': 'Processed result'}

        response = self.client.post(url, data_from_consumer)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.message.refresh_from_db()
        self.assertEqual(self.message.result, 'Processed result')

    def test_webhook_receiver_view_missing_message_id(self):
        url = reverse('webhook-receiver')
        data_from_consumer = {'result': 'Processed result'}

        response = self.client.post(url, data_from_consumer)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Message.objects.get(pk=self.message.id).result, None)

    def test_webhook_receiver_view_message_not_found(self):
        url = reverse('webhook-receiver')
        data_from_consumer = {'message_id': 999, 'result': 'Processed result'}

        response = self.client.post(url, data_from_consumer)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_webhook_receiver_view_missing_result_data(self):
        url = reverse('webhook-receiver')
        data_from_consumer = {'message_id': self.message.id}

        response = self.client.post(url, data_from_consumer)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Message.objects.get(pk=self.message.id).result, None)


