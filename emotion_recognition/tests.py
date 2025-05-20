from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import AudioRecord, EmotionResult
import tempfile
import os


class EmotionRecognitionTests(TestCase):
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        
        # Create a temporary audio file
        self.temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
        self.temp_file.close()
        
        # Create test audio record
        self.audio_record = AudioRecord.objects.create(
            user=self.user,
            file_path=self.temp_file.name,
            source='upload'
        )
        
        # Create test emotion result
        self.emotion_result = EmotionResult.objects.create(
            audio_record=self.audio_record,
            emotion='happy',
            confidence=0.85
        )
    
    def tearDown(self):
        # Remove temporary file
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
    
    def test_user_login(self):
        # Test login functionality
        response = self.client.post(reverse('emotion_recognition:login'), {
            'username': 'testuser',
            'password': 'testpassword'
        })
        self.assertRedirects(response, reverse('emotion_recognition:dashboard'))
    
    def test_index_page(self):
        # Test index page renders correctly
        response = self.client.get(reverse('emotion_recognition:index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'emotion_recognition/index.html')
    
    def test_dashboard_requires_login(self):
        # Test dashboard requires authentication
        response = self.client.get(reverse('emotion_recognition:dashboard'))
        self.assertRedirects(response, f"{reverse('emotion_recognition:login')}?next={reverse('emotion_recognition:dashboard')}")
        
        # Login and try again
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('emotion_recognition:dashboard'))
        self.assertEqual(response.status_code, 200)
