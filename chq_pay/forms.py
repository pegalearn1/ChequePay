from django import forms
from .models import Banks, Currencies, Payee

#reset password

from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.conf import settings




class BankForm(forms.ModelForm):
    class Meta:
        model = Banks
        fields = ['bank_char', 'bank_name_e', 'bank_name_l', 'tel_no', 'address']
        labels = {
            'bank_char': 'Bank Characters',
            'bank_name_e': 'Bank Name (English)',
            'bank_name_l': 'Bank Name (Local)',
            'tel_no': 'Telephone Number',
            'address': 'Bank Address',
        }

        help_texts = {
            'bank_char': 'Enter a unique short identifier for the bank.',
            'bank_name_e': 'Enter the official English name of the bank.',
            'bank_name_l': 'Enter the local language name of the bank, if applicable.',
            'tel_no': 'Provide a contact number with country code if necessary.',
            'address': 'Enter the address of the bank.',
        }

        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }


class CurrencyForm(forms.ModelForm):
    class Meta:
        model = Currencies
        fields = ['currency_char', 'currency_name']
        labels = {
            'currency_char': 'Currency Characters',
            'currency_name': 'Currency Name',
        }
        help_texts = {
            'currency_char': 'Enter the short code for the currency (e.g., USD, EUR, INR).',
            'currency_name': 'Enter the full name of the currency (e.g., US Dollar, Euro, Indian Rupee).',
        }


class PayeeForm(forms.ModelForm):
    class Meta:
        model = Payee
        fields = ['payee_name', 'mobile_no', 'email', 'address']
        labels = {
            'payee_name': 'Payee Name',
            'mobile_no': 'Mobile Number',
            'email': 'Email',
            'address': 'Address',
        }
        help_texts = {
            'payee_name': 'Enter the full name of the payee.',
            'mobile_no': 'Provide the mobile number with country code if applicable.',
            'email': 'Enter a valid email address for the payee.',
            'address': 'Enter the complete postal address of the payee.',
        }
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }





User = get_user_model()

class CustomPasswordResetForm(PasswordResetForm):
    reg_code = forms.CharField(max_length=10, required=True, label="Company Code")

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        reg_code = cleaned_data.get('reg_code')

        print("Debug - reg_code:", reg_code)  # Check input
        print("Debug - email:", email)

        # Check if reg_code is in settings.DATABASES
        if reg_code not in settings.DATABASES:
            raise ValidationError("Invalid Registration Code. Please check and try again.")
        
        # Fetch the user query result once
        query_result = User.objects.using(reg_code).filter(email=email)

        # Debug: Print actual database query being executed
        print("Debug - Query SQL:", str(query_result.query))  # Check the actual query

        # Check if the user exists in the specified database
        if not query_result.exists():
            print("Debug - User NOT FOUND in", reg_code)  # Debugging
            raise ValidationError("No user with this email exists for the provided Company Code.")
        else:
            print("Debug - User FOUND in", reg_code)

        return cleaned_data

    def save(self, *args, **kwargs):
        reg_code = self.cleaned_data['reg_code']
        email = self.cleaned_data['email']

        print(f"🔍 Sending password reset email for {email} using DB: {reg_code}")

        kwargs['use_https'] = False
        kwargs['extra_email_context'] = {'database': reg_code}

        # Patch: Temporarily override get_users to use correct DB
        original_get_users = self.get_users
        def custom_get_users(email):
            return User.objects.using(reg_code).filter(email__iexact=email, is_active=True)
        self.get_users = custom_get_users

        try:
            print("📨 About to call super().save() to trigger email...")
            super().save(*args, **kwargs)
            print("✅ Password reset email function executed!")
        except Exception as e:
            print(f"❌ Error sending email: {e}")
        finally:
            self.get_users = original_get_users  # Restore original


