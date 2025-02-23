import os
from google.oauth2 import service_account
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Configuración de GCP
GS_CREDENTIALS = service_account.Credentials.from_service_account_file(
    'vlp-web-service-account-key.json'  # Asegúrate de tener este archivo
)
GS_BUCKET_NAME = 'vulpis.com.ar'
GS_PROJECT_ID = 'vlp-web'

# Configurar el backend de almacenamiento
DEFAULT_FILE_STORAGE = 'storages.backends.gcloud.GoogleCloudStorage'
STATICFILES_STORAGE = 'storages.backends.gcloud.GoogleCloudStorage'

# Configuración de archivos estáticos
STATIC_URL = f'https://storage.googleapis.com/{GS_BUCKET_NAME}/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# Configuración de archivos media
MEDIA_URL = f'https://storage.googleapis.com/{GS_BUCKET_NAME}/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Asegurarse de que las carpetas existan
os.makedirs(STATIC_ROOT, exist_ok=True)
os.makedirs(MEDIA_ROOT, exist_ok=True)

# Configuración adicional necesaria para producción
DEBUG = False
ALLOWED_HOSTS = ['vlp-web.appspot.com', 'vulpis.com.ar']

# Configuración de seguridad
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'vlp_web_db',
        'USER': 'postgres',
        'PASSWORD': 'AdminVlp01A$2025',
        'HOST': '/cloudsql/vlp-web:us-central1:vlp-web-db',
    }
} 