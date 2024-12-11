from django.db import models
from django.contrib.auth.models import AbstractUser


#Abstract User profile

class ChqpayUser(AbstractUser):
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    civil_id = models.CharField(max_length=20, unique=True, null=True, blank=True)
    privilege_char = models.CharField(max_length=50, null=True, blank=True)  # or use choices for predefined roles

    def __str__(self):
        return self.username



##########################################################################################################################################################################################################################################################

#bank models

class Banks(models.Model):
    bank_char = models.CharField(max_length=10)
    bank_name_e = models.CharField(max_length=120)
    bank_name_l = models.CharField(max_length=120)
    tel_no = models.CharField(max_length=20)
    address = models.TextField()
    created_by = models.IntegerField()
    created_date = models.DateTimeField()
    modified_by = models.IntegerField()
    modified_date = models.DateTimeField()

    def __str__(self):
        return self.bank_char

##########################################################################################################################################################################################################################################################

#currency models

class Currencies(models.Model):
    currency_char = models.CharField(max_length=5)
    currency_name = models.CharField(max_length=100)
    created_by = models.IntegerField()
    created_date = models.DateTimeField()
    modified_by = models.IntegerField()
    modified_date = models.DateTimeField()

    def __str__(self):
        return self.currency_char
    

#########################################################################################################################################################################################################################################################

#company_setup

class Company_Setup(models.Model):
    registration_id = models.CharField(max_length=50)
    company_name = models.CharField(max_length=120)
    logo = models.ImageField(upload_to ='company_logos/', blank = True, null=True )
    tax_id = models.CharField(max_length=120, null=True, blank=True)
    currency_id = models.IntegerField()
    tel_no = models.CharField(max_length=20)
    email = models.EmailField(max_length=100)
    address = models.TextField(blank=True, null=True)
    created_by = models.IntegerField()
    created_date = models.DateTimeField()
    modified_by = models.IntegerField()
    modified_date = models.DateTimeField()

    def __str__(self):
        return self.company_name

#########################################################################################################################################################################################################################################################

#Payee

class Payee(models.Model):
    payee_name = models.CharField(max_length=120)
    mobile_no = models.CharField(max_length=20)
    email = models.EmailField(max_length=100)
    created_by = models.IntegerField()
    created_date = models.DateTimeField()
    modified_by = models.IntegerField()
    modified_date = models.DateTimeField()

    def __str__(self):
        return self.payee_name



##########################################################################################################################################################################################################################################################

#Cheque Models
#to add and save the cheque template
class ChequeTemplate(models.Model):
    name = models.CharField(max_length=100, help_text="*Name of the cheque template")
    width = models.FloatField(help_text="*Width of the cheque in mm")
    height = models.FloatField(help_text="*Height of the cheque in mm")
    background_image = models.ImageField(upload_to='cheque_templates/', help_text="*Upload the cheque background image")
    created_by = models.IntegerField()
    created_date = models.DateTimeField()
    modified_by = models.IntegerField()
    modified_date = models.DateTimeField()

    def __str__(self):
        return self.name
    
############
#to set the text on the cheque template
class ChequeText(models.Model):
    template = models.ForeignKey(ChequeTemplate, on_delete=models.CASCADE)
    text = models.CharField(max_length=255, help_text="Text to be printed on the cheque")
    x_position = models.FloatField(help_text="X position of the text in mm")
    y_position = models.FloatField(help_text="Y position of the text in mm")
    created_by = models.IntegerField()
    created_date = models.DateTimeField()
    modified_by = models.IntegerField()
    modified_date = models.DateTimeField()

    def __str__(self):
        return f"{self.text} on {self.template.name}"
    
##########################################################################################################################################################################################################################################################