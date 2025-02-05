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
    payees = ChequeIssue.objects.values('issue_payee__id','issue_payee__payee_name', 'issue_payee__mobile_no','issue_payee__email','issue_payee__address').distinct()

    
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

        if selected_payees:
            # Initialize a dictionary to group cheques by payee
            payee_cheques = {}

            # Fetch cheques filtered by the selected payees
            for payee in selected_payees:
                print("\n")
                print("payee - ", payee)
                # Filter cheques by the current payee
                chq_payee = cheques.filter(issue_payee=payee)

                # Group cheques by payee
                for p in chq_payee:
                    if p.issue_payee.payee_name not in payee_cheques:
                        payee_cheques[p.issue_payee.payee_name] = []
                    payee_cheques[p.issue_payee.payee_name].append(p)

            # Iterate over the payee_cheques dictionary to print each payee's name and associated cheque details
            for payee_name, cheques in payee_cheques.items():
                print(f"Payee: {payee_name}")
                
                for p in cheques:
                    print(f"Cheque Details - Bank: {p.issue_bank.bank_name_e}, Amount: {p.issue_amount}")  # Adjust as per your model's fields
           

            # After the loop, render the template with the gathered `all_chq_payees`
            return render(request, "Reports/payee_report.html", {'chq_payee': payee_cheques.items()})
                
        
        # print("payeeesss -- ", chq_payee)
        # print("acountsss -- ", selected_accounts)
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