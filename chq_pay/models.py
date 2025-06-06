from django.db import models
from django.contrib.auth.models import AbstractUser
from decimal import ROUND_DOWN, Decimal

##########################################################################################################################################################################################################################################################

#Abstract User profile

class ChqpayUser(AbstractUser):
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    privilege_role = models.CharField(max_length=30, null=True, blank=True)  # or use choices for predefined roles
    auth_sign = models.ImageField(upload_to ='Signatures/', blank = True, null=True )
    
    def __str__(self):
        return self.username

##########################################################################################################################################################################################################################################################
#company_setup

class Company_Setup(models.Model):
    registration_id = models.CharField(max_length=50)
    company_name = models.CharField(max_length=120)
    logo = models.ImageField(upload_to ='company_logos/', blank = True, null=True )
    tax_id = models.CharField(max_length=120, null=True, blank=True)
    is_selected = models.BooleanField()
    # currency_id = models.IntegerField()
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


#bank models

class Banks(models.Model):
    bank_char = models.CharField(max_length=10)
    bank_name_e = models.CharField(max_length=120)
    bank_name_l = models.CharField(max_length=120, blank=True, null=True)
    tel_no = models.CharField(max_length=20, blank= True, null= True)
    address = models.TextField(blank= True, null= True)
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



#Payee

class Payee(models.Model):
    payee_name = models.CharField(max_length=120)
    payee_bank = models.ForeignKey(Banks, on_delete=models.CASCADE, null=True, blank=True)
    payee_acc_no = models.IntegerField(null=True, blank=True)
    mobile_no = models.CharField(max_length=20, blank= True, null= True)
    email = models.EmailField(max_length=100, blank= True, null= True)
    address = models.TextField(null=True, blank=True)
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
    company = models.ForeignKey(Company_Setup, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, help_text="*Name of the cheque template")
    bank = models.ForeignKey(Banks, on_delete=models.CASCADE)
    currency = models.ForeignKey(Currencies, on_delete=models.CASCADE)
    width = models.FloatField(help_text="*Width of the cheque in mm")
    height = models.FloatField(help_text="*Height of the cheque in mm")
    background_image = models.ImageField(upload_to='cheque_templates/', help_text="*Upload the cheque background image")
    payee_char_limit = models.IntegerField(blank=True, null=True)
    amount_char_limit = models.IntegerField(blank=True, null=True)
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

    date_x_position = models.FloatField(null=True, blank=True)
    date_y_position = models.FloatField(null=True, blank=True)
    date_font = models.CharField(max_length=100, null=True, blank=True)
    date_size = models.CharField(max_length=10, null=True, blank=True)
    date_bold = models.BooleanField(default=False)
    date_italic = models.BooleanField(default=False)

    payee_x_position = models.FloatField(null=True, blank=True)
    payee_y_position = models.FloatField(null=True, blank=True)
    payee_font = models.CharField(max_length=100, null=True, blank=True)
    payee_size = models.CharField(max_length=10, null=True, blank=True)
    payee_bold = models.BooleanField(default=False)
    payee_italic = models.BooleanField(default=False)

    amtwrds_x_position = models.FloatField(null=True, blank=True)
    amtwrds_y_position = models.FloatField(null=True, blank=True)
    amtwrds_font = models.CharField(max_length=100, null=True, blank=True)
    amtwrds_size = models.CharField(max_length=10, null=True, blank=True)
    amtwrds_bold = models.BooleanField(default=False)
    amtwrds_italic = models.BooleanField(default=False)

    amtnum_x_position = models.FloatField(null=True, blank=True)
    amtnum_y_position = models.FloatField(null=True, blank=True)
    amtnum_font = models.CharField(max_length=100, null=True, blank=True)
    amtnum_size = models.CharField(max_length=10, null=True, blank=True)
    amtnum_bold = models.BooleanField(default=False)
    amtnum_italic = models.BooleanField(default=False)

    sign_x_position = models.FloatField(null=True, blank=True)
    sign_y_position = models.FloatField(null=True, blank=True)
    

    created_by = models.IntegerField()
    created_date = models.DateTimeField()
    modified_by = models.IntegerField()
    modified_date = models.DateTimeField()


    def __str__(self):
        return f"{self.text} on {self.template.name}"
    
##########################################################################################################################################################################################################################################################
#Cheque Issue Model
class ChequeIssue(models.Model):
    company = models.ForeignKey(Company_Setup, on_delete=models.CASCADE)
    issue_template = models.ForeignKey(ChequeTemplate, on_delete=models.CASCADE)
    issue_accountnum = models.IntegerField()
    issue_cheque_no = models.IntegerField()
    issue_currency = models.ForeignKey(Currencies, on_delete=models.CASCADE)
    issue_cheque_date = models.DateField()
    issue_payee = models.ForeignKey(Payee, on_delete=models.CASCADE)
    issue_bank = models.ForeignKey(Banks, on_delete=models.CASCADE)
    issue_amount = models.DecimalField(max_digits=30, decimal_places=3)
    issue_naration = models.CharField(max_length=200)
    issue_issue_date = models.DateField()
    issue_sign = models.BooleanField(null=True, blank=True)
    issue_is_approved = models.BooleanField(null=True, blank=True)
    issue_approv_rejectby = models.IntegerField(null=True, blank=True)
    created_by = models.IntegerField()
    created_date = models.DateTimeField()
    modified_by = models.IntegerField()
    modified_date = models.DateTimeField()


##########################################################################################################################################################################################################################################################

class AppUser(models.Model):
    reg_code = models.IntegerField()
    license_key = models.CharField(max_length=100)
    name = models.CharField(max_length=200)
    email = models.CharField(max_length=100)
    cust_id = models.CharField(max_length=200)
    country_id = models.IntegerField()
    country_name = models.CharField(max_length=100)
    allowed_templates = models.IntegerField()
    expiry_date = models.CharField(max_length=50)




##########################################################################################################################################################################################################################################################

#to save all temprary data
class TempDatas(models.Model):
    session_id = models.CharField(max_length=255, unique=True)
    data = models.JSONField()  # Stores JSON data
    created_at = models.DateTimeField(auto_now_add=True)