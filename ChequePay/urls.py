"""
URL configuration for ChequePay project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from chq_pay.forms import CustomPasswordResetForm

urlpatterns = [
    path('admin/', admin.site.urls),
    path('Chequepay/', include('chq_pay.urls')),
     # Password Reset
     path('password_reset/', auth_views.PasswordResetView.as_view(
        template_name='Password_Reset/password_reset_form.html',
        email_template_name='Password_Reset/password_reset_email.html',
        subject_template_name='Password_Reset/password_reset_subject.txt',
        success_url='/password_reset_done/',
        form_class=CustomPasswordResetForm  # Use the custom form
    ), name='password_reset'),
    path('password_reset_done/', auth_views.PasswordResetDoneView.as_view(
        template_name='Password_Reset/password_reset_done.html'
    ), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='Password_Reset/password_reset_confirm.html',
        success_url='/password_reset_complete/'
    ), name='password_reset_confirm'),
    path('password_reset_complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='Password_Reset/password_reset_complete.html'
    ), name='password_reset_complete'),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# # Serve media files during development
# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)