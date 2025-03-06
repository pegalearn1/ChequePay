from django import forms
from .models import Banks, Currencies, Payee


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

