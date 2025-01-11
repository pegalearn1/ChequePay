''' The Project 'Cheque Printer' is solely created by Faraz Ahmed Raj - Python Developer
in 2024-2025.'''

from .imp_libs import *
from chq_pay.models import Banks, Payee, ChequeTemplate, ChequeIssue

def home(request):
    return render(request, "home/home.html")

@login_required
def base_temp(request):
    return render(request, "layouts/base.html")

@login_required
def index(request):
    bank_count = Banks.objects.count()
    payee_count = Payee.objects.count()
    template_count = ChequeTemplate.objects.count()
    chq_issue_count = ChequeIssue.objects.count()

    context = {
        'bank_count':bank_count,
        'payee_count':payee_count,
        'template_count':template_count,
        'chq_issue_count':chq_issue_count
        }



    return render(request, "home/index.html", context)


def profile(request):
    return render(request, "home/profile.html")

