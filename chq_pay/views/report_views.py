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
        else:
            messages.warning(request,"No Records found for the given parameters" )
            return redirect('reports')

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


            # Initialize dictionaries to store cumulative sums by currency
            summary_total_approved = {}
            summary_total_pending = {}
            summary_total_rejected = {}
            

            # Fetch cheques filtered by the selected payees
            chq_payees = cheques.filter(issue_payee__in=selected_payees)
            summary_total_payee = len(selected_payees)

            # Process approved cheques
            for cheque in chq_payees.filter(issue_is_approved=True):
                currency = cheque.issue_currency.currency_char
                summary_total_approved[currency] = summary_total_approved.get(currency, 0) + (cheque.issue_amount if currency == 'KWD' else round(cheque.issue_amount, 2))

            # Process pending cheques
            for cheque in chq_payees.filter(issue_is_approved=None):
                currency = cheque.issue_currency.currency_char
                summary_total_pending[currency] = summary_total_pending.get(currency, 0) + (cheque.issue_amount if currency == 'KWD' else round(cheque.issue_amount, 2))

            # Process rejected cheques
            for cheque in chq_payees.filter(issue_is_approved=False):
                currency = cheque.issue_currency.currency_char
                summary_total_rejected[currency] = summary_total_rejected.get(currency, 0) + (cheque.issue_amount if currency == 'KWD' else round(cheque.issue_amount, 2))

            
            
            # Initialize a dictionary to group cheques by payee
            payee_cheques = {}
            

            # Fetch cheques filtered by the selected payees
            for payee in selected_payees:
                
                chq_payee = cheques.filter(issue_payee=payee)
                

                payee_name = Payee.objects.filter(id=payee).values_list('payee_name', flat=True).first()

                total_approved = {}

                for p in chq_payee:
                    if payee_name not in payee_cheques:
                        payee_cheques[payee_name] = []
                    payee_cheques[payee_name].append(p)

                    # Sum approved cheque amounts per currency for each payee
                    if p.issue_is_approved:
                        currency = p.issue_currency.currency_char
                        if currency not in total_approved:
                            total_approved[currency] = 0
                        total_approved[currency] += (p.issue_amount if currency == 'KWD' else round(p.issue_amount, 2))

                if selected_approval == 'approved' or selected_approval == '':
                    # Store total amounts in a separate variable and append the results
                    payee_cheques[payee_name].append({"total_approved": total_approved})

            
            context = {
                'chq_payee': payee_cheques.items(),
                'company':company,
                 'bank':bank_name,
                 'approval':approval,
                 'st_date':st_date,
                 'ed_date':ed_date,
                 'summary_total_payee':summary_total_payee,
                 'summary_approved_amt':summary_total_approved.items(),
                 'summary_pending_amt':summary_total_pending.items(),
                 'summary_rejected_amt':summary_total_rejected.items()
                 
            }
            
            # After the loop, render the template with the gathered `all_chq_payees`
            return render(request, "Reports/payee_report.html", context)

        else:
            messages.warning(request, "Please select some records") 
        

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



@login_required
def export_payee_report(request, file_format):
    # Fetch filtered cheques from session (or reapply filters)
    selected_payees = request.GET.getlist('selected_payees')

    print("payees - ", selected_payees)
    selected_bank = request.GET.get('bank', '')
    selected_approval = request.GET.get('approval', '')
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')

    cheques = ChequeIssue.objects.all().filter(Q(company__is_selected=True)).order_by('-issue_cheque_date')

    # Apply filters
    if selected_bank:
        cheques = cheques.filter(issue_bank__id=selected_bank)
    if selected_approval:
        if selected_approval == 'approved':
            cheques = cheques.filter(issue_is_approved=True)
        elif selected_approval == 'pending':
            cheques = cheques.filter(issue_is_approved=None)
        elif selected_approval == 'rejected':
            cheques = cheques.filter(issue_is_approved=False)
    if start_date and end_date:
        cheques = cheques.filter(issue_cheque_date__range=[start_date, end_date])
    if selected_payees:
        cheques = cheques.filter(issue_payee__in=selected_payees)

    # Data to export
    data = [
        ["Payee Name", "Bank", "Account#", "Cheque#", "Amount", "Currency", "Cheque Date", "Approval"]
    ]
    for chq in cheques:

        issue_amount = f"{chq.issue_amount:.3f}" if chq.issue_currency.currency_char == 'KWD' else f"{chq.issue_amount:.2f}"


        data.append([
            chq.issue_payee.payee_name,
            chq.issue_bank.bank_name_e,
            chq.issue_accountnum,
            chq.issue_cheque_no,
            issue_amount,
            chq.issue_currency.currency_char,
            chq.issue_cheque_date.strftime('%Y-%m-%d'),
            "Approved" if chq.issue_is_approved else "Pending" if chq.issue_is_approved is None else "Rejected",
        ])

    # Export as CSV
    if file_format == "csv":
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="payee_report.csv"'
        writer = csv.writer(response)
        for row in data:
            writer.writerow(row)
        return response

    # Export as XLS (Excel)
    elif file_format == "xls":
        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = 'attachment; filename="payee_report.xls"'
        workbook = xlwt.Workbook()
        sheet = workbook.add_sheet('Payee Report')

        for row_num, row_data in enumerate(data):
            for col_num, cell_data in enumerate(row_data):
                sheet.write(row_num, col_num, cell_data)
        
        workbook.save(response)
        return response

    # Export as XLSX (Newer Excel format)
    elif file_format == "xlsx":
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="payee_report.xlsx"'
        workbook = openpyxl.Workbook()
        sheet = workbook.active
        sheet.title = "Payee Report"

        for row in data:
            sheet.append(row)

        workbook.save(response)
        return response

    else:
        return HttpResponse("Invalid file format", status=400)