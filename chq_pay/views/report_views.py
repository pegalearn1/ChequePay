''' The Project 'Cheque Printer' is solely created by Faraz Ahmed Raj - Python Developer
in 2024-2025.'''

from .imp_libs import *
from chq_pay.models import ChequeTemplate, ChequeText, Banks, Currencies, Payee, ChequeIssue, Company_Setup

#user model
User = get_user_model()

@login_required
def reports(request):
    cheques = ChequeIssue.objects.all().filter(Q(company__is_selected=True)).order_by('-issue_cheque_date')
    banks = ChequeIssue.objects.values_list('issue_bank__id','issue_bank__bank_name_e').distinct()
    accounts = ChequeIssue.objects.values_list('issue_accountnum', 'issue_bank__bank_name_e').distinct()
    payees = ChequeIssue.objects.select_related('issue_payee').distinct()

    
    # Fetch filter parameters for Bank and Approval
    selected_bank = request.POST.get('bank', '')
    selected_approval = request.POST.get('approval', '')
    start_date = request.POST.get('start_date', '')
    end_date = request.POST.get('end_date', '')

    
    # Filter by bank
    if selected_bank:
        cheques = cheques.filter(issue_bank__id=selected_bank)

    # Filter by approval status
    if selected_approval:
        if selected_approval == 'approved':
            cheques = cheques.filter(issue_is_approved=True)
        elif selected_approval == 'pending':
            cheques = cheques.filter(issue_is_approved=None)
        elif selected_approval == 'rejected':
            cheques = cheques.filter(issue_is_approved=False)

    # Filter by cheque date range
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

    
    # If POST request, get selected checkboxes
    if request.method == 'POST':
        selected_payees = request.POST.getlist('selected_payees')
        selected_accounts = request.POST.getlist('selected_accounts')

        print("payeeesss -- ", selected_payees)
        print("acountsss -- ", selected_accounts)
        print("getbanks - ", selected_bank)
        print("getapproval - ", selected_approval)
        print("getstdate - ", start_date)
        print("geteddate - ", end_date)

    # Context for the template
    context = {
        'cheques': cheques,
        'banks': banks,
        'accounts': accounts,
        'payees': payees,
        'sel_bank':int(selected_bank) if selected_bank else None,
        'approval': selected_approval,
        'start_date': start_date,
        'end_date': end_date,
    }

    return render(request,  "Reports/reports.html", context)