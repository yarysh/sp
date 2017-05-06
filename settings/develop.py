from .base import *

DEBUG = True
SECRET_KEY = 'o=2t-+0c_b9fm1s@d-+-a)=0$=yzf8(zck0*p7w((xnj^p5qv!'
ALLOWED_HOSTS = ['*']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

SMS_GATES = {
    'SMSC': {
        'HOST': 'http://smsc.ru/sys/send.php',
        'USER': '*****',
        'PASSWORD': '*****',
        'PARAMS': {'fmt': 3, 'charset': 'utf-8'}
    },
    'SMSTraffic': {
        'HOST': 'http://smstraffic.ru/superapi/message/',
        'USER': '',
        'PASSWORD': '',
        'PARAMS': {}
    },
}