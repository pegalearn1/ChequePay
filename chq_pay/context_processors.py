from .models import Company_Setup

def global_companies(request):
    companies = Company_Setup.objects.all()
    return {'companies': companies}
