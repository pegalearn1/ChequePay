''' The Project 'Cheque Printer' is solely created by Faraz Ahmed Raj - Python Developer
in 2024-2025.'''

from .imp_libs import *
from chq_pay.models import ChequeTemplate, ChequeText, Banks, Currencies, Payee, ChequeIssue, Company_Setup

#user model
User = get_user_model()

@login_required
def reports(request):
    cheques = ChequeIssue.objects.all().filter(Q(company__is_selected=True)).order_by('-issue_cheque_date')
    templates = ChequeTemplate.objects.all()
    banks = Banks.objects.all()
    accounts = ChequeIssue.objects.values_list('issue_accountnum', flat=True).distinct()
    payees = Payee.objects.all()
    chq_txts = ChequeText.objects.all()

    print("accountsss - ", accounts)

    # Apply filters if provided in the request
    search = request.GET.get('search', '')
    if search:
        cheques = cheques.filter(
            Q(issue_accountnum__icontains=search) |
            Q(issue_payee__payee_name__icontains=search) |
            Q(issue_cheque_no__icontains=search) |
             Q(issue_template__name__icontains=search)
        )

     # Fetch filter parameters for Bank And Currency
    selected_bank = request.GET.get('bank')
    selected_currency = request.GET.get('currency')
    
    if selected_bank:
        cheques = cheques.filter(issue_bank__id=selected_bank)
    if selected_currency:
        cheques = cheques.filter(issue_currency__id=selected_currency)

    # Filter by approval status
    approval = request.GET.get('approval', '')
    if approval:
        if approval == 'approved':
            cheques = cheques.filter(issue_is_approved=True)
        elif approval == 'pending':
            cheques = cheques.filter(issue_is_approved=None)
        elif approval == 'rejected':
            cheques = cheques.filter(issue_is_approved=False)

    # Filter by cheque date range
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')
    if start_date and end_date:
        cheques = cheques.filter(issue_cheque_date__range=[start_date, end_date])

    # Fetch the user who approved or rejected the cheque
    for chq in cheques:
        try:
            usr = User.objects.filter(id=chq.issue_approv_rejectby)
            for us in usr:
                chq.app_rej_by = us.first_name
        except User.DoesNotExist:
            chq.user_first_name = None


    # Context for the template
    context = {
        'cheques': cheques,
        'templates': templates,
        'banks': banks,
        'accounts': accounts,
        'payees': payees,
        'chq_txts': chq_txts,
        'search': search,
        'approval': approval,
        'start_date': start_date,
        'end_date': end_date,
    }

    return render(request,  "Reports/reports.html", context)