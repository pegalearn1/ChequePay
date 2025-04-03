from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent

DATABASES = {
    '3151': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR/'chqpaydb_3151.sqlite3',
    },
    '3122': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR/'chqpaydb_3122.sqlite3',
    },
    '3156': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR/'chqpaydb_3156.sqlite3',
    },
    '3154': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR/'chqpaydb_3154.sqlite3',
    },
    '3117': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR/'chqpaydb_3117.sqlite3',
    },
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'chqpaydb.sqlite3',
    }
}