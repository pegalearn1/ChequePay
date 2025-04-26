import os
import django
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ChequePay.settings')
django.setup()

from ChequePay.db_config import DATABASES

def migrate_database(db_name):
    print(f"Running migrations for database: {db_name}")
    os.system(f"python manage.py migrate --database={db_name}")

if __name__ == '__main__':
    for db in DATABASES.keys():
        migrate_database(db)

    print("\n✅ All migrations completed.")
