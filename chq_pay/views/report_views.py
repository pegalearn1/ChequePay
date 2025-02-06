''' The Project 'Cheque Printer' is solely created by Faraz Ahmed Raj - Python Developer
in 2024-2025.'''

from .imp_libs import *
from chq_pay.models import ChequeTemplate, ChequeText, Banks, Currencies, Payee, ChequeIssue, Company_Setup
from django.db.models import Sum
#user model
User = get_user_model()

@login_required
def reports(request):
    cheques = ChequeIssue.objects.all().filter(Q(company__is_selected=True)).order_by('-issue_cheque_date')
    banks = ChequeIssue.objects.filter(Q(company__is_selected=True)).values_list('issue_bank__id','issue_bank__bank_name_e').distinct()
    accounts = ChequeIssue.objects.filter(Q(company__is_selected=True)).values_list('issue_accountnum', 'issue_bank__bank_name_e').distinct()
    payees = ChequeIssue.objects.filter(Q(company__is_selected=True)).values('issue_payee__id','issue_payee__payee_name', 'issue_payee__mobile_no','issue_payee__email','issue_payee__address').distinct()

    
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
        company = Company_Setup.objects.filter(is_selected = True).first()
        
        bank_name = 'All'
        approval = 'All'
        st_date = None
        ed_date = None
        if selected_bank:
            bank = Banks.objects.filter(id = selected_bank).values('bank_name_e').first()
            bank_name = bank['bank_name_e']
        if selected_approval:
            approval = selected_approval.title()
        if start_date and end_date:
            st_date = start_date
            ed_date = end_date

        
        if selected_payees:
            # Initialize a dictionary to group cheques by payee
            payee_cheques = {}
            payee_total_approved_amounts = {}
            

            # Fetch cheques filtered by the selected payees
            for payee in selected_payees:
                
                chq_payee = cheques.filter(issue_payee=payee)

                total_approved = {}

                for p in chq_payee:
                    if p.issue_payee.payee_name not in payee_cheques:
                        payee_cheques[p.issue_payee.payee_name] = []
                    payee_cheques[p.issue_payee.payee_name].append(p)

                    # Sum approved cheque amounts per currency for each payee
                    if p.issue_is_approved:
                        currency = p.issue_currency.currency_char
                        if currency not in total_approved:
                            total_approved[currency] = 0
                        total_approved[currency] += p.issue_amount

                    # Store total amounts in the payee_cheques dictionary
                    payee_cheques[p.issue_payee.payee_name].append({"total_approved": total_approved})

                print("payee cheques - ", payee_cheques.items())
                

            # # Iterate over the payee_cheques dictionary to print each payee's name and associated cheque details
            # for payee_name, cheques in payee_cheques.items():
            #     print(f"Payee: {payee_name}")
                
            #     for p in cheques:
            #         print(f"Cheque Details - Bank: {p.issue_bank.bank_name_e}, Amount: {p.issue_amount}")  # Adjust as per your model's fields
           

            context = {
                'chq_payee': payee_cheques.items(),
                'company':company,
                 'bank':bank_name,
                 'approval':approval,
                 'st_date':st_date,
                 'ed_date':ed_date


            }
            
            # After the loop, render the template with the gathered `all_chq_payees`
            return render(request, "Reports/payee_report.html", context)
                
        
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