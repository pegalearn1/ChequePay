from django.core.mail import send_mail
from django.conf import settings

send_mail(
    'Test Password check',
    'Check if the password email is sent',
    settings.EMAIL_HOST_USER,
    ['pegalearn1@gmail.com'],
    fail_silently=False,
)
