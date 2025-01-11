from .models import Company_Setup

def global_companies(request):
    companies = Company_Setup.objects.all().order_by('created_date')
    return {'companies': companies}
