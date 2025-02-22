from google.oauth2 import service_account

# Configuración de GCP
GS_CREDENTIALS = service_account.Credentials.from_service_account_file(
    'path/to/your/service-account-key.json'
)
GS_BUCKET_NAME = 'your-bucket-name'
GS_PROJECT_ID = 'your-project-id'

# Configurar el backend de almacenamiento
DEFAULT_FILE_STORAGE = 'storages.backends.gcloud.GoogleCloudStorage'
STATICFILES_STORAGE = 'storages.backends.gcloud.GoogleCloudStorage'

# URLs para archivos estáticos y media
STATIC_URL = f'https://storage.googleapis.com/{GS_BUCKET_NAME}/static/'
MEDIA_URL = f'https://storage.googleapis.com/{GS_BUCKET_NAME}/media/'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'your-database-name',
        'USER': 'your-database-user',
        'PASSWORD': 'your-database-password',
        'HOST': '/cloudsql/your-connection-name',
    }
} 