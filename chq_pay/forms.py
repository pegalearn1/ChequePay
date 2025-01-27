from django import forms
from .models import Banks, Currencies, Payee


class BankForm(forms.ModelForm):
    class Meta:
        model = Banks
        fields = ['bank_char', 'bank_name_e', 'bank_name_l', 'tel_no', 'address']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }


class CurrencyForm(forms.ModelForm):
    class Meta:
        model = Currencies
        fields = ['currency_char', 'currency_name']


class PayeeForm(forms.ModelForm):
    class Meta:
        model = Payee
        fields = ['payee_name', 'mobile_no', 'email', 'address']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }
