from .models import Company_Setup, AppUser
from django.db import connection

def global_companies(request):
      
    # print("Context Processor DB in use:", connection.settings_dict['NAME'])  # Debug

    companies = Company_Setup.objects.all().order_by('created_date')
    return {'companies': companies}


def license_info(request):
    license = AppUser.objects.all()
    return {'license': license}

