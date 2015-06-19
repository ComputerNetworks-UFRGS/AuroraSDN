from settings import *
DATABASES['default']['USER'] = 'postgres'
DATABASES['default']['PASSWORD'] = 'postgres'
STATIC_ROOT = '/home/phisolani/Dropbox/Mestrado/Aurora/static/'
MEDIA_ROOT = '/home/phisolani/Dropbox/Mestrado/Aurora/sdn/'
LOGGING['handlers']['file']['filename'] = '/home/phisolani/Dropbox/Mestrado/Aurora/logs/main.log'

ADMINS = (
   ('Pedro Heleno Isolani', 'phisolani@inf.ufrgs.br'),
)

GOOGLE_OAUTH2_CLIENT_ID = '848614648179.apps.googleusercontent.com'
GOOGLE_OAUTH2_CLIENT_SECRET = 'Bssy8AWgW-WcGqV9NnkCnqxF'
