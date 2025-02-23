from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import Video

# Create your tests here.

class VideoUploadTest(TestCase):
    def setUp(self):
        # Crear un usuario de prueba
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client = Client()
        
    def test_video_upload(self):
        # Login
        self.client.login(username='testuser', password='testpass123')
        
        # Crear un archivo de prueba
        video_content = b'test video content'
        video_file = SimpleUploadedFile(
            "test_video.mp4",
            video_content,
            content_type="video/mp4"
        )
        
        # Intentar subir el video
        response = self.client.post('/upload/', {
            'video_file': video_file,
            'title': 'Test Video'
        })
        
        # Verificar que la subida fue exitosa
        self.assertEqual(response.status_code, 302)  # Redirección después de subir
        self.assertTrue(Video.objects.filter(title='Test Video').exists())
