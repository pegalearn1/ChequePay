from .models import Company_Setup, AppUser

def global_companies(request):
    companies = Company_Setup.objects.all().order_by('created_date')
    return {'companies': companies}


def license_info(request):
    license = AppUser.objects.all()
    return {'license': license}

