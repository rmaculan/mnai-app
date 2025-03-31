from django.test import TestCase, Client
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from .models import Conversation, Chat
import json

class ConversationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.other_user = User.objects.create_user(username='otheruser', password='12345')
        self.conversation = Conversation.objects.create(
            title='Test Conversation',
            user=self.user,
            provider='openai'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_create_conversation(self):
        url = '/chatbot/api/conversations/'
        data = {'title': 'New Conversation', 'provider': 'openai'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Conversation.objects.count(), 2)

    def test_list_conversations(self):
        url = '/chatbot/api/conversations/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_retrieve_conversation(self):
        url = f'/chatbot/api/conversations/{self.conversation.id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Conversation')

    def test_update_conversation(self):
        url = f'/chatbot/api/conversations/{self.conversation.id}/'
        data = {'title': 'Updated Title'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.conversation.refresh_from_db()
        self.assertEqual(self.conversation.title, 'Updated Title')

    def test_delete_conversation(self):
        url = f'/chatbot/api/conversations/{self.conversation.id}/'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.conversation.refresh_from_db()
        self.assertIsNotNone(self.conversation.deleted_at)
        self.assertFalse(self.conversation.is_active)

    def test_other_user_cannot_access(self):
        self.client.force_authenticate(user=self.other_user)
        url = f'/chatbot/api/conversations/{self.conversation.id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_archive_conversation(self):
        url = f'/chatbot/api/conversations/{self.conversation.id}/archive/'
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.conversation.refresh_from_db()
        self.assertTrue(self.conversation.is_archived)

    def test_pin_conversation(self):
        url = f'/chatbot/api/conversations/{self.conversation.id}/pin/'
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.conversation.refresh_from_db()
        self.assertTrue(self.conversation.is_pinned)

    def test_favorite_conversation(self):
        url = f'/chatbot/api/conversations/{self.conversation.id}/favorite/'
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.conversation.refresh_from_db()
        self.assertTrue(self.conversation.is_favorite)

    def test_toggle_archive_conversation(self):
        url = f'/chatbot/api/conversations/{self.conversation.id}/archive/'
        # First archive
        response = self.client.post(url)
        self.conversation.refresh_from_db()
        self.assertTrue(self.conversation.is_archived)
        # Then unarchive
        response = self.client.post(url)
        self.conversation.refresh_from_db()
        self.assertFalse(self.conversation.is_archived)

class ChatTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.conversation = Conversation.objects.create(
            title='Test Conversation',
            user=self.user,
            provider='openai'
        )
        self.chat = Chat.objects.create(
            conversation=self.conversation,
            user=self.user,
            message='Test message',
            response='Test response'
        )
        self.client = Client()
        self.client.login(username='testuser', password='12345')

    def test_chat_creation(self):
        url = '/chatbot/'
        data = {'message': 'Hello'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Chat.objects.count(), 2)

    def test_chat_history(self):
        url = '/chatbot/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test message')
