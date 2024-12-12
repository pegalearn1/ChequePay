''' The Project 'Cheque Printer' is solely created by Faraz Ahmed Raj - Python Developer
in 2024-2025.'''

from .imp_libs import *
from chq_pay.models import ChequeTemplate, ChequeText, Banks, Currencies, Payee, ChequeIssue

def cheque_issue(request):
    if request.method == 'POST':
        issue_template = request.POST.get('chq_template')
        issue_cheque_no = request.POST.get('chq_no')
        issue_cheque_date = request.POST.get('chq_date')
        issue_payee = request.POST.get('chq_payee')
        issue_amount = request.POST.get('chq_amt')
        issue_naration = request.POST.get('chq_narration')
        issue_sign = request.FILES.get('chq_sign')
        
        # print("POST - ", request.POST)


        # Save the data to the database
        cheque_issue_temp = get_object_or_404(ChequeTemplate, id = issue_template)
        issue_amount_wrd = num2words(issue_amount)



        try:
            cheque_issue_new = ChequeIssue(
                issue_template=cheque_issue_temp,
                issue_cheque_no=issue_cheque_no,
                issue_currency= get_object_or_404(Currencies, id = cheque_issue_temp.currency.id),
                issue_cheque_date = issue_cheque_date,
                issue_payee = get_object_or_404(Payee, id = issue_payee),
                issue_bank=get_object_or_404(Banks, id = cheque_issue_temp.bank.id),
                issue_amount = issue_amount,
                issue_amount_wrd = issue_amount_wrd +''+'only',
                issue_issue_date=date.today(),
                issue_naration=issue_naration,
                issue_sign=issue_sign,
                created_by = request.user.id,
                created_date = datetime.now(),
                modified_by = request.user.id,
                modified_date = datetime.now()

            )

            print("cheque currency - ", get_object_or_404(ChequeTemplate, id = issue_template) )

            

            cheque_issued = ChequeIssue.objects.filter(issue_payee=issue_payee, issue_cheque_no=issue_cheque_no,issue_cheque_date=issue_cheque_date)

            if cheque_issued:
                messages.error(request,('Cheque Already Issued!!'))
            else:
                cheque_issue_new.save()
                messages.success(request,('Cheque Issued Successfully!!!'))
                
                response = ({"success": True})
                print("responseee = ",response)
                return JsonResponse(response)
        except Exception as e:
            print("error : ",str(e))
    return JsonResponse({"success": False})

def cheque_issue_list(request):
    cheques = ChequeIssue.objects.all()
    templates = ChequeTemplate.objects.all()
    banks = Banks.objects.all()
    currencies = Currencies.objects.all()
    payees = Payee.objects.all()


    context = {'cheques':cheques,
               'templates': templates,
               'banks':banks,
               'currencies':currencies,
               'payees':payees}
    return render(request, 'Cheque_issue/cheque_issue_list.html', context )

def delete_chequeissue(request, chequeissue_id):
    cheque_issue = get_object_or_404(ChequeIssue, id=chequeissue_id)
    cheque_issue.delete()
    messages.error(request,('Cheque Issued Deleted Successfully!!'))
    return redirect('cheque_issue_list')


def edit_template(request):
    if request.method == "POST":
        template_id = request.POST.get("template_id")
        name = request.POST.get('name')
        width = request.POST.get('width')
        height = request.POST.get('height')
        bank = request.POST.get('bank')
        currency = request.POST.get('currency')
        background_image = request.FILES.get('background_image')

        print("currency_id - ",template_id)
        
        # Update the bank in the database
        try:
            template = ChequeTemplate.objects.get(id=template_id)
            template.name = name
            template.width = width
            template.height = height
            template.bank = get_object_or_404(Banks, id=bank)
            template.currency = get_object_or_404(Currencies, id=currency)
            template.background_image = background_image
            template.modified_by = request.user.id
            template.modified_date = datetime.now()

            template_exist = ChequeTemplate.objects.filter(name=name).exclude(id=template_id)

            if template_exist:
                messages.error(request,('Currency with same name or Currency Char already exits!!'))

            else:
                
                template.save()
                messages.success(request,('Template Details Updated Successfully!!!'))
                return JsonResponse({"success": True})
        except ChequeTemplate.DoesNotExist:
            return JsonResponse({"success": False, "error": "Currency not found"})
    return JsonResponse({"success": False, "error": "Invalid request"})


