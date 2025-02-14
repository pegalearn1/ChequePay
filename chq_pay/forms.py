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


class PayeeForm(forms.ModelForm):
    class Meta:
        model = Payee
        fields = ['payee_name', 'mobile_no', 'email', 'address']
        labels = {
            'payee_name': 'Payee Name',
            'mobile_no':'Mobile Number',
            'email':'Email',
            'address':'Address'
        }
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }
