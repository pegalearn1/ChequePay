''' The Project 'Cheque Printer' is solely created by Faraz Ahmed Raj - Python Developer
in 2024-2025.'''

from .imp_libs import *
from chq_pay.models import Banks, Payee, ChequeTemplate, ChequeIssue, Currencies

def home(request):
    return render(request, "home/home.html")

@login_required
def base_temp(request):
    return render(request, "layouts/base.html")

@login_required
def index(request):
#for certain counts
    bank_count = Banks.objects.count()
    payee_count = Payee.objects.count()
    template_count = ChequeTemplate.objects.count()
    currency_count = Currencies.objects.count()
    
#for cheque counts
    total_cheques = ChequeIssue.objects.count()
    approved_cheques = ChequeIssue.objects.filter(issue_is_approved = True).count()
    pending_cheques = ChequeIssue.objects.filter(issue_is_approved = None).count()
    rejected_cheques = ChequeIssue.objects.filter(issue_is_approved = False).count()

#for cheque issue  pie chart
    #chart cheque issue & bank template labels
    banks = Banks.objects.order_by('bank_name_e')
    bank_names = list(banks.values_list('bank_name_e', flat=True))
   
    #chart cheque issue values
    chq_iss = []
    for bnk in banks:
        iss_chq = ChequeIssue.objects.filter(issue_bank = bnk).filter(issue_is_approved = True).count()
        chq_iss.append(str(iss_chq))

    cheque_issued = ','.join(chq_iss)

    #pie chart colors for cheque issue
    cheque_issue_color = []
    for chq_color in range(approved_cheques):
        random_color = (randrange(255), randrange(255), randrange(255))
        cheque_issue_color.append(f'rgb({random_color[0]}, {random_color[1]}, {random_color[2]})')



#for bank template pie chart
    #chart bank template values
    chq_temps = []
    for bnk in banks:
        bank_temps = ChequeTemplate.objects.filter(bank = bnk).count()
        chq_temps.append(str(bank_temps))

    bank_templates = ','.join(chq_temps)

    #pie chart colors for bank template
    template_color = []
    for temp_color in range(template_count):
        random_color = (randrange(255), randrange(255), randrange(255))
        template_color.append(f'rgb({random_color[0]}, {random_color[1]}, {random_color[2]})')



#for currency-transact-pie  pie chart
    #chart currency-transact labels
    currencies = Currencies.objects.order_by('currency_char')
    currency_char = list(currencies.values_list('currency_char', flat=True))
   
    #chart currency-transact values
    cur_transct = []
    for cur in currencies:
        currency_transact = ChequeIssue.objects.filter(issue_bank = bnk).filter(issue_currency = cur).values_list('issue_amount', flat=True)
        cur_transct.append(str(currency_transact))

    currency_transctions = ','.join(chq_iss)

    #pie chart colors for currency-transact
    currency_trans_color = []
    for cur_color in range(currency_count):
        random_color = (randrange(255), randrange(255), randrange(255))
        currency_trans_color.append(f'rgb({random_color[0]}, {random_color[1]}, {random_color[2]})')


    




    
    
    context = {
        'bank_count':bank_count,
        'payee_count':payee_count,
        'template_count':template_count,
        'currency_count':currency_count,
        'chq_issue_count':approved_cheques,
        'bank_names':bank_names,
        'cheque_issued':cheque_issued,
        'cheque_issue_colors':cheque_issue_color,
        'bank_templates':bank_templates,
        'template_color':template_color,
        'total_cheques':total_cheques,
        'approved_cheques':approved_cheques,
        'pending_cheques':pending_cheques,
        'rejected_cheques':rejected_cheques,
        'currency_char':currency_char,
        'currency_trans_color':currency_trans_color,




        }



    return render(request, "home/index.html", context)


def profile(request):
    return render(request, "home/profile.html")

