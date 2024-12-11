from django import forms
from chq_pay.models import ChequeTemplate, ChequeText

class ChequeTemplateForm(forms.ModelForm):
    class Meta:
        model = ChequeTemplate
        fields = ['name', 'width', 'height', 'background_image']
        labels = {
            'name': 'Cheque Template Name',
            'width': 'Cheque Width (mm)',
            'height': 'Cheque Height (mm)',
            'background_image': 'Cheque Background Image',
        }

        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Enter cheque template name',
                'style': 'max-width: 400px; width: 100%;'  # Limit width
            }),
            'width': forms.NumberInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Enter width in millimeters',
                'style': 'max-width: 150px; width: 100%;'  # Limit width
            }),
            'height': forms.NumberInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Enter height in millimeters',
                'style': 'max-width: 150px; width: 100%;'  # Limit width
            }),
            'background_image': forms.ClearableFileInput(attrs={
                'class': 'form-control-file',
                'style': 'max-width: 400px; width: 100%;'  # Limit width
            }),
        }

    def __init__(self, *args, **kwargs):
        super(ChequeTemplateForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.label = field.label.upper()  # Optional: make label uppercase
            field.widget.attrs['style'] = 'font-weight: bold;'  # Apply bold style to labels

class ChequeTextForm(forms.ModelForm):
    class Meta:
        model = ChequeText
        fields = ['text']
        labels = {
            'text': 'Text to Add on Cheque',
        }
