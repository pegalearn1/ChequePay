from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent

DATABASES = {
    '3117': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR/'chqpaydb_3117.sqlite3',
    },
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'chqpaydb.sqlite3',
    }
}