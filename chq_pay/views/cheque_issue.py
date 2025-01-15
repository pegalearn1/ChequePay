''' The Project 'Cheque Printer' is solely created by Faraz Ahmed Raj - Python Developer
in 2024-2025.'''

from .imp_libs import *
from chq_pay.models import ChequeTemplate, ChequeText, Banks, Currencies, Payee, ChequeIssue, Company_Setup

#user model
User = get_user_model()



def amount_in_words(amount, currency, lang):
    """
    Convert a numeric amount into words for a given currency and language.
    Args:
        amount (float): The numeric amount.
        currency (str): The currency code (e.g., "INR", "KWD").
        lang (str): The language code (e.g., "en", "hi", "ar").
    Returns:
        str: The amount in words.
    """
    amount_parts = str(amount).split('.')
    whole_part = int(amount_parts[0])
    fractional_part = int(amount_parts[1]) if len(amount_parts) > 1 else 0

    if currency == "INR" and lang == "en":  # Indian Rupees in Hindi
        rupees = num2words(whole_part, lang="en")
        if fractional_part > 0:
            paise = num2words(fractional_part, lang="en")
            return f"{rupees} Rupees and {paise} Paise"
        return f"{rupees} Rupees"
    
    elif currency == "INR" and lang == "hi":  # Indian Rupees in Hindi
        rupees = num2words(whole_part, lang="hi")
        if fractional_part > 0:
            paise = num2words(fractional_part, lang="hi")
            return f"{rupees} रुपये और {paise} पैसे"
        return f"{rupees} रुपये"

    elif currency == "KWD" and lang == "en":  # Kuwaiti Dinar in English
        dinars = num2words(whole_part, lang="en")
        if fractional_part > 0:
            fils = num2words(fractional_part, lang="en")
            return f"{dinars} Dinar and {fils} Fils"
        return f"{dinars} Dinar"

    elif currency == "KWD" and lang == "ar":  # Kuwaiti Dinar in Arabic
        dinars = num2words(whole_part, lang="ar")
        if fractional_part > 0:
            fils = num2words(fractional_part, lang="ar")
            return f"{dinars} دينار كويتي و {fils} فلس"
        return f"{dinars} دينار كويتي"
    
    elif currency == "USD" and lang == "en":  # US Dollars in English
        dollars = num2words(whole_part, lang="en")
        if fractional_part > 0:
            cents = num2words(fractional_part, lang="en")
            result = f"{dollars} Dollars And {cents} Cents"
        else:
            result = f"{dollars} Dollars"

    elif currency == "EUR" and lang == "en":  # Euros in English
        euros = num2words(whole_part, lang="en")
        if fractional_part > 0:
            cents = num2words(fractional_part, lang="en")
            result = f"{euros} Euros And {cents} Cents"
        else:
            result = f"{euros} Euros"

    elif currency == "AED" and lang == "en":  # UAE Dirhams in Arabic
        dirhams = num2words(whole_part, lang="en")
        if fractional_part > 0:
            fils = num2words(fractional_part, lang="en")
            result = f"{dirhams} Dirhams And {fils} Fils"
        else:
            result = f"{dirhams} Dirhams"
    
    
    elif currency == "AED" and lang == "ar":  # UAE Dirhams in Arabic
        dirhams = num2words(whole_part, lang="ar")
        if fractional_part > 0:
            fils = num2words(fractional_part, lang="ar")
            result = f"{dirhams} درهم إماراتي و {fils} فلس"
        else:
            result = f"{dirhams} درهم إماراتي"

    elif currency == "SAR" and lang == "en":  # Saudi Riyals in Arabic
        riyals = num2words(whole_part, lang="en")
        if fractional_part > 0:
            halalas = num2words(fractional_part, lang="en")
            result = f"{riyals} Riyals And {halalas} Halala"
        else:
            result = f"{riyals} ريال سعودي"
    
    elif currency == "SAR" and lang == "ar":  # Saudi Riyals in Arabic
        riyals = num2words(whole_part, lang="ar")
        if fractional_part > 0:
            halalas = num2words(fractional_part, lang="ar")
            result = f"{riyals} ريال سعودي و {halalas} هللة"
        else:
            result = f"{riyals} ريال سعودي"

    else:
        raise ValueError(f"Unsupported currency {currency} or language {lang}")



@login_required
def cheque_issue(request):
    if request.method == 'POST':
        issue_template = request.POST.get('chq_template')
        issue_cheque_no = request.POST.get('chq_no')
        issue_cheque_date = request.POST.get('chq_date')
        issue_payee = request.POST.get('chq_payee')
        issue_amount = request.POST.get('chq_amt')
        issue_naration = request.POST.get('chq_narration')
        issue_sign = request.FILES.get('chq_sign')

        if issue_sign:
            issue_sign = issue_sign
        
        
        # Save the data to the database
        comapny_now = get_object_or_404(Company_Setup, is_selected = True)
        cheque_issue_temp = get_object_or_404(ChequeTemplate, id = issue_template)
        issue_currency = get_object_or_404(Currencies, id = cheque_issue_temp.currency.id)
        issue_currency_char = issue_currency.currency_char
        issue_amount_wrd = amount_in_words(issue_amount, issue_currency_char, 'en')
        issue_amount_wrd_title = issue_amount_wrd.title()

        print(issue_amount_wrd)



        try:
            cheque_issue_new = ChequeIssue(
                company = comapny_now,
                issue_template=cheque_issue_temp,
                issue_cheque_no=issue_cheque_no,
                issue_currency= issue_currency,
                issue_cheque_date = issue_cheque_date,
                issue_payee = get_object_or_404(Payee, id = issue_payee),
                issue_bank=get_object_or_404(Banks, id = cheque_issue_temp.bank.id),
                issue_amount = issue_amount,
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

@login_required
def cheque_issue_list(request):
    cheques = ChequeIssue.objects.all().filter(Q(company__is_selected=True)).order_by('-issue_cheque_date')
    templates = ChequeTemplate.objects.all()
    banks = Banks.objects.all()
    currencies = Currencies.objects.all()
    payees = Payee.objects.all()
    chq_txts = ChequeText.objects.all()

    for chq in cheques:
        try:
            usr = User.objects.filter(id = chq.issue_approv_rejectby)
            for us in usr:
                chq.app_rej_by = us.first_name
           
        except User.DoesNotExist:
             chq.user_first_name = None


    #pagination
    per_page = 25
    paginator = Paginator(cheques, per_page)
    page_number = request.GET.get('page')
    cheques_issued = paginator.get_page(page_number)
    #pagination


    context = {'cheques':cheques_issued,
               'templates': templates,
               'banks':banks,
               'currencies':currencies,
               'payees':payees,
               'chq_txts':chq_txts}
    return render(request, 'Cheque_issue/cheque_issue_list.html', context )


@login_required
def delete_chequeissue(request, chequeissue_id):
    cheque_issue = get_object_or_404(ChequeIssue, id=chequeissue_id)
    cheque_issue.delete()
    messages.error(request,('Cheque Issued Deleted Successfully!!'))
    return redirect('cheque_issue_list')



@login_required
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




@login_required
def get_cheque_text(request):
    template_id = request.GET.get('template_id')

    if not template_id:
        return JsonResponse({'error': 'Template ID is required'}, status=400)
    
    try:
        cheque_text = ChequeText.objects.get(template=template_id)
        data = {
            'date_x': cheque_text.date_x_position,
            'date_y': cheque_text.date_y_position,
            'payee_x': cheque_text.payee_x_position,
            'payee_y': cheque_text.payee_y_position,
            'amtwrds_x': cheque_text.amtwrds_x_position,
            'amtwrds_y': cheque_text.amtwrds_y_position,
            'amtnum_x': cheque_text.amtnum_x_position,
            'amtnum_y': cheque_text.amtnum_y_position,
            'sign_x': cheque_text.sign_x_position,
            'sign_y': cheque_text.sign_y_position,
        }
        return JsonResponse({'data': data}, status=200)
    except ChequeText.DoesNotExist:
        return JsonResponse({'error': 'Cheque text not found for this template'}, status=404)
    


@login_required
@csrf_exempt
def print_cheque(request, cheque_id):
    cheque_issue = get_object_or_404(ChequeIssue, id=cheque_id)
    isapproved = cheque_issue.issue_is_approved
    template = cheque_issue.issue_template
    try:
        cheque_text = get_object_or_404(ChequeText, template=template)
    except Exception as e:
        messages.error(request, 'Set Text Positions On Template First.')
        return redirect('cheque_issue_list')  # You should redirect or render an error page
    
    issue_currency = cheque_issue.issue_currency.currency_char

    if request.method == "POST":
        # Process language selection
        data = json.loads(request.body)

        print("dataaa - ", data)


        selected_language = data.get("language", "ar")

        print("request pst - ", selected_language)
        # Generate the amount in words in the selected language
        issue_amount_wrd = amount_in_words(cheque_issue.issue_amount, issue_currency, selected_language)
        issue_amount_wrd_title = issue_amount_wrd.title()

        
        # Return only the updated "amount in words"
        return JsonResponse({
            "success": True,
            "amount_word": '*' + '*' + issue_amount_wrd_title + '*' + '*',
        })
    
        

    # Handle GET request (initial page load)
    issue_amount_wrd = amount_in_words(
        cheque_issue.issue_amount, issue_currency, 'ar'
    )
    issue_amount_wrd_title = issue_amount_wrd.title()

    context = {
        'template': template.background_image,
        'width': template.width,
        'height': template.height,
        'date': '  '.join([char for char in cheque_issue.issue_cheque_date.strftime('%d%m%Y')]),
        'payee': '*' + '*' + cheque_issue.issue_payee.payee_name + '*' + '*',
        'amount': '*' + '*' + str(cheque_issue.issue_amount) + '*' + '*',
        'amount_word': '*' + '*' + issue_amount_wrd_title + '*' + '*',
        'positions': {
            'date': (cheque_text.date_x_position, cheque_text.date_y_position),
            'payee': (cheque_text.payee_x_position, cheque_text.payee_y_position),
            'amount_word': (cheque_text.amtwrds_x_position, cheque_text.amtwrds_y_position),
            'amount_num': (cheque_text.amtnum_x_position, cheque_text.amtnum_y_position),
            'sign': (cheque_text.sign_x_position, cheque_text.sign_y_position),
        },
        'sign_url': cheque_issue.issue_sign.url if cheque_issue.issue_sign else None,
        'cheque_id': cheque_id,
        'issue_currency':issue_currency,
        
        }
    return render(request, 'Cheque_issue/print_cheque.html', context)


def approval(request, cheque_id):

    additional_value = request.GET.get('additional_value')

    print("add val - ", additional_value)

    cheque_issue = get_object_or_404(ChequeIssue, id=cheque_id)
    if cheque_issue.issue_is_approved is None and additional_value == "True":
        cheque_issue.issue_is_approved = True
        cheque_issue.issue_approv_rejectby = request.user.id
        cheque_issue.modified_by = request.user.id
        cheque_issue.modified_date = datetime.now()
        messages.success(request, 'Cheque is Approved.')
    
    elif cheque_issue.issue_is_approved is None and additional_value == "False":
        cheque_issue.issue_is_approved = False
        cheque_issue.issue_approv_rejectby = request.user.id
        cheque_issue.modified_by = request.user.id
        cheque_issue.modified_date = datetime.now()
        messages.success(request, 'Cheque is Rejected.')
    
    elif cheque_issue.issue_is_approved == False:
        cheque_issue.issue_is_approved = True
        cheque_issue.issue_approv_rejectby = request.user.id
        cheque_issue.modified_by = request.user.id
        cheque_issue.modified_date = datetime.now()
        messages.success(request, 'Cheque is Approved.')
    
    elif cheque_issue.issue_is_approved == True:
        cheque_issue.issue_is_approved = False
        cheque_issue.issue_approv_rejectby = request.user.id
        cheque_issue.modified_by = request.user.id
        cheque_issue.modified_date = datetime.now()
        messages.error(request, 'Cheque is Rejected.')

    cheque_issue.save()

    previous_url = request.META.get('HTTP_REFERER')

    return redirect(previous_url)



    
    
