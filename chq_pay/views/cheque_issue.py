''' The Project 'Cheque Printer' is solely created by Faraz Ahmed Raj - Python Developer
in 2024-2025.'''

from .imp_libs import *
from chq_pay.models import ChequeTemplate, ChequeText, Banks, Currencies, Payee, ChequeIssue, Company_Setup
from decimal import Decimal, ROUND_DOWN
from chq_pay.views.currency_lists import currency_data
#user model
User = get_user_model()


# #To convert the amount to words
# def amount_in_words(amount, currency, lang):
#     """
#     Convert a numeric amount into words for a given currency and language.
#     Args:
#         amount (float): The numeric amount.
#         currency (str): The currency code (e.g., "INR", "KWD").
#         lang (str): The language code (e.g., "en", "hi", "ar").
#     Returns:
#         str: The amount in words.
#     """
#     amount_parts = str(amount).split('.')
#     whole_part = int(amount_parts[0])
#     fractional_part = int(amount_parts[1]) if len(amount_parts) > 1 else 0

#     if currency == "INR" and lang == "en":  # Indian Rupees in Hindi
#         rupees = num2words(whole_part, lang="en")
#         if fractional_part > 0:
#             paise = num2words(fractional_part, lang="en")
#             return f"{rupees} Rupees and {paise} Paise"
#         return f"{rupees} Rupees"
    
#     elif currency == "INR" and lang == "hi":  # Indian Rupees in Hindi
#         rupees = num2words(whole_part, lang="hi")
#         if fractional_part > 0:
#             paise = num2words(fractional_part, lang="hi")
#             return f"{rupees} रुपये और {paise} पैसे"
#         return f"{rupees} रुपये"

#     elif currency == "KWD" and lang == "en":  # Kuwaiti Dinar in English
#         dinars = num2words(whole_part, lang="en")
#         if fractional_part > 0:
#             fils = num2words(fractional_part, lang="en")
#             return f"{dinars} Dinar and {fils} Fils"
#         return f"{dinars} Dinar"

#     elif currency == "KWD" and lang == "ar":  # Kuwaiti Dinar in Arabic
#         dinars = num2words(whole_part, lang="ar")
#         if fractional_part > 0:
#             fils = num2words(fractional_part, lang="ar")
#             return f"{dinars} دينار كويتي و {fils} فلس"
#         return f"{dinars} دينار كويتي"
    
#     elif currency == "USD" and lang == "en":  # US Dollars in English
#         dollars = num2words(whole_part, lang="en")
#         if fractional_part > 0:
#             cents = num2words(fractional_part, lang="en")
#             result = f"{dollars} Dollars And {cents} Cents"
#         else:
#             result = f"{dollars} Dollars"

#         return result

#     elif currency == "EUR" and lang == "en":  # Euros in English
#         euros = num2words(whole_part, lang="en")
#         if fractional_part > 0:
#             cents = num2words(fractional_part, lang="en")
#             result = f"{euros} Euros And {cents} Cents"
#         else:
#             result = f"{euros} Euros"

#         return result

#     elif currency == "AED" and lang == "en":  # UAE Dirhams in Arabic
#         dirhams = num2words(whole_part, lang="en")
#         if fractional_part > 0:
#             fils = num2words(fractional_part, lang="en")
#             result = f"{dirhams} Dirhams And {fils} Fils"
#         else:
#             result = f"{dirhams} Dirhams"

#         return result
    
    
#     elif currency == "AED" and lang == "ar":  # UAE Dirhams in Arabic
#         dirhams = num2words(whole_part, lang="ar")
#         if fractional_part > 0:
#             fils = num2words(fractional_part, lang="ar")
#             result = f"{dirhams} درهم إماراتي و {fils} فلس"
#         else:
#             result = f"{dirhams} درهم إماراتي"

#         return result

#     elif currency == "SAR" and lang == "en":  # Saudi Riyals in Arabic
#         riyals = num2words(whole_part, lang="en")
#         if fractional_part > 0:
#             halalas = num2words(fractional_part, lang="en")
#             result = f"{riyals} Riyals And {halalas} Halala"
#         else:
#             result = f"{riyals} ريال سعودي"

#         return result
    
#     elif currency == "SAR" and lang == "ar":  # Saudi Riyals in Arabic
#         riyals = num2words(whole_part, lang="ar")
#         if fractional_part > 0:
#             halalas = num2words(fractional_part, lang="ar")
#             result = f"{riyals} ريال سعودي و {halalas} هللة"
#         else:
#             result = f"{riyals} ريال سعودي"

#         return result

#     else:
#         raise ValueError(f"Unsupported currency {currency} or language {lang}")


def amount_in_words(amount, currency, lang):
    amount_parts = str(amount).split('.')
    whole_part = int(amount_parts[0])
    fractional_part = int(amount_parts[1]) if len(amount_parts) > 1 else 0

    # Get currency info or fallback
    info = currency_data.get(currency, {
        "main": {lang: currency},
        "sub": {lang: ""}
    })

    main_unit = info['main'].get(lang, currency)
    sub_unit = info['sub'].get(lang, "")

    try:
        whole_word = num2words(whole_part, lang=lang).title()
        fractional_word = num2words(fractional_part, lang=lang).title() if fractional_part > 0 else ""
    except NotImplementedError:
        raise ValueError(f"Language '{lang}' is not supported for conversion.")

    if fractional_part > 0:
        connector = {
            "en": "and",
            "hi": "और",
            "ar": "و"
        }.get(lang, "and")
        return f"{whole_word} {main_unit} {connector} {fractional_word} {sub_unit}".strip()
    else:
        return f"{whole_word} {main_unit}".strip()

        
    

#to split the words for payee or amount in words in two lines
def split_text_preserving_words(text: str, max_line_length: int = 52) -> str:
    """
    Splits the given text into two lines without breaking words,
    where the first line fits within max_line_length characters.

    Args:
        text (str): The text to be split.
        max_line_length (int): Max character length for the first line.

    Returns:
        str: The formatted text with two lines.
    """
    words = text.split()
    first_line = ''
    second_line = ''
    current_len = 0

    for word in words:
        # +1 accounts for the space if first_line already has content
        if current_len + len(word) + (1 if current_len > 0 else 0) <= max_line_length:
            if first_line:
                first_line += ' '
            first_line += word
            current_len = len(first_line)
        else:
            if second_line:
                second_line += ' '
            second_line += word

    return first_line + '\n' + second_line


def convert_arabic_to_english_number(arabic_number_str):
    arabic_to_english = str.maketrans("٠١٢٣٤٥٦٧٨٩٫", "0123456789.")
    return arabic_number_str.translate(arabic_to_english)





@login_required
def cheque_issue(request):
    if request.method == 'POST':
        issue_template = request.POST.get('chq_template')
        issue_accountnum = request.POST.get('acc_no')
        issue_cheque_no = request.POST.get('chq_no')
        issue_cheque_date = request.POST.get('chq_date')
        issue_payee = request.POST.get('chq_payee')
        issue_amount = request.POST.get('chq_amt')
        issue_naration = request.POST.get('chq_narration')
        issue_sign = request.POST.get('chq_sign')

        if issue_sign == "on":
            issue_sign = True
        else:
            issue_sign = False

        issue_amount_clean = convert_arabic_to_english_number(issue_amount)

        print("issue amount - ", issue_amount)
        print("issue amount clean - ", issue_amount_clean)

        
        # Save the data to the database
        comapny_now = get_object_or_404(Company_Setup, is_selected = True)
        cheque_issue_temp = get_object_or_404(ChequeTemplate, id = issue_template)
        issue_currency = get_object_or_404(Currencies, id = cheque_issue_temp.currency.id)
        issue_currency_char = issue_currency.currency_char
        issue_amount_wrd = amount_in_words(issue_amount_clean, issue_currency_char, 'en')
        

        if cheque_issue_temp.currency.currency_char != "KWD":
            issue_amount = Decimal(issue_amount_clean).quantize(Decimal("0.01"), rounding=ROUND_DOWN)



        try:
            cheque_issue_new = ChequeIssue(
                company = comapny_now,
                issue_template=cheque_issue_temp,
                issue_accountnum = issue_accountnum,
                issue_cheque_no=issue_cheque_no,
                issue_currency= issue_currency,
                issue_cheque_date = issue_cheque_date,
                issue_payee = (get_object_or_404(Payee, id = issue_payee)),
                issue_bank=get_object_or_404(Banks, id = cheque_issue_temp.bank.id),
                issue_amount = issue_amount_clean,
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
                messages.warning(request,('Cheque Already Issued!!'))
            else:
                cheque_issue_new.save()
                messages.success(request,('Cheque Issued Successfully!!!'))
                
                response = ({"success": True})
                print("responseee = ",response)
                return JsonResponse(response)
        except Exception as e:
            messages.error(request,('Cheque Issued Failed!! : ', str(e)))
            print("error : ",str(e))
    return JsonResponse({"success": False})

@login_required
def cheque_issue_list(request):
    cheques = ChequeIssue.objects.all().filter(company__is_selected=True).order_by('-created_date')
    templates = ChequeTemplate.objects.all()
    banks = Banks.objects.all()
    currencies = Currencies.objects.all()
    payees = Payee.objects.all()
    chq_txts = ChequeText.objects.all()

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
        elif approval == 'all':
            cheques = cheques
        elif approval == 'rejected':
            cheques = cheques.filter(issue_is_approved=False)
        elif approval == 'pending':
            cheques = cheques.filter(issue_is_approved=None)
    else:
        cheques = cheques.filter(issue_is_approved=None)


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

    # Pagination
    per_page = 25
    paginator = Paginator(cheques, per_page)
    page_number = request.GET.get('page')
    cheques_issued = paginator.get_page(page_number)

    for x in cheques:
        print('chequee - ', x.issue_amount)

    # Context for the template
    context = {
        'cheques': cheques_issued,
        'templates': templates,
        'banks': banks,
        'currencies': currencies,
        'payees': payees,
        'chq_txts': chq_txts,
        'search': search,
        'approval': approval,
        'start_date': start_date,
        'end_date': end_date,
    }
    return render(request, 'Cheque_issue/cheque_issue_list.html', context)


@login_required
def delete_chequeissue(request, chequeissue_id):
    
    # Get the previous URL from the request
    previous_url = request.META.get('HTTP_REFERER', '/')

    cheque_issue = get_object_or_404(ChequeIssue, id=chequeissue_id)
    cheque_issue.delete()
    messages.success(request,('Cheque Issued Deleted Successfully!!'))
    return redirect(previous_url)



@login_required
def edit_cheque_issue(request):
    if request.method == 'POST':
        issue_template = request.POST.get('chq_template')
        issue_accountnum = request.POST.get('acc_no')
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
                issue_accountnum = issue_accountnum,
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
                messages.warning(request,('Cheque Already Issued!!'))
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
    

#To preview the cheque and print it
@login_required
@csrf_exempt
def print_cheque(request, cheque_id):
    sign_url = None  # Initialize with a default value
    cheque_issue = get_object_or_404(ChequeIssue, id=cheque_id)
    isapproved = cheque_issue.issue_is_approved
    template = cheque_issue.issue_template
    try:
        cheque_text = get_object_or_404(ChequeText, template=template)
    except Exception as e:
        messages.error(request, 'Set Text Positions On Template First.')
        return redirect('cheque_issue_list')  # You should redirect or render an error page
    
    issue_currency = cheque_issue.issue_currency.currency_char

    #to format the decimals according to the currency 
    if cheque_issue.issue_currency.currency_char != "KWD":
        issue_amount = "{:.2f}".format(cheque_issue.issue_amount)
    else:
        issue_amount = cheque_issue.issue_amount

    if request.method == "POST":
        try:
            data = json.loads(request.body)
            
            # Language change
            if "language" in data:
                selected_language = data.get("language", "en")
                issue_amount_wrd = amount_in_words(issue_amount, issue_currency, selected_language)
                issue_amount_wrd_title = issue_amount_wrd.title()
                if selected_language == "ar":
                    # Add فقط at the beginning and لا غير at the end
                    ammmt = '**فقط ' + issue_amount_wrd_title + ' لا غير**'
                else:
                    ammmt = '**' + issue_amount_wrd_title + ' Only' + '**'

                if template.amount_char_limit not in [None, '']:
                    formatted_amount_word = split_text_preserving_words(ammmt, max_line_length=template.amount_char_limit)
                else:
                    formatted_amount_word = split_text_preserving_words(ammmt)

                return JsonResponse({
                    "success": True,
                    "amount_word": formatted_amount_word,
                })
            

             # Date format change
            if "date_format" in data:
                selected_format = data.get("date_format", "spaced")
                
                if selected_format == "spaced":
                    formatted_date = '  '.join([char for char in cheque_issue.issue_cheque_date.strftime('%d%m%Y')])
                elif selected_format == "date-spaced":
                    formatted_date = cheque_issue.issue_cheque_date.strftime('%d %m %Y')
                elif selected_format == "slashed":
                    formatted_date = cheque_issue.issue_cheque_date.strftime('%d/%m/%Y')
                elif selected_format == "dashed":
                    formatted_date = cheque_issue.issue_cheque_date.strftime('%d-%m-%Y')

                return JsonResponse({
                    "success": True,
                    "date": formatted_date,
                })

            return JsonResponse({"success": False, "error": "Invalid request."}, status=400)

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=400)
    
        

    # Handle GET request (initial page load)
    issue_amount_wrd = amount_in_words(
        issue_amount, issue_currency, 'en'
    )

    issue_amount_wrd_title = issue_amount_wrd.title()

    print("amount in words chars", template.amount_char_limit)

    ammmt = '**' + issue_amount_wrd_title + ' Only' + '**'
    
    if template.amount_char_limit not in [None, '']:
        formatted_amount_word = split_text_preserving_words(ammmt, max_line_length=template.amount_char_limit)
    else:
        formatted_amount_word = split_text_preserving_words(ammmt)

    print("Formatted Amount Word:", formatted_amount_word)

    #Format the payee name if the character limit exceeds
    payee_name = '*' + '*' + cheque_issue.issue_payee.payee_name + '*' + '*'

    if template.payee_char_limit not in [None, '']:
        formatted_payee_name = split_text_preserving_words(payee_name, max_line_length=template.payee_char_limit)
    else:
        formatted_payee_name = split_text_preserving_words(payee_name)
    
    print("Formatted Payee Name:", formatted_payee_name)    
    
    if cheque_issue.issue_sign and isapproved:
        aprvd_by = cheque_issue.issue_approv_rejectby
        usr = User.objects.filter(id=aprvd_by).first()

        if usr and usr.auth_sign:
            sign_url = request.build_absolute_uri(usr.auth_sign.url)
            print("Signature URL:", sign_url)
        else:
            messages.error(request, 'Signature is not uploaded, please upload a signature image via profile.')
            return redirect(request.META.get('HTTP_REFERER'))


    context = {
        'template': template.background_image,
        'width': template.width,
        'height': template.height,
        'date': '  '.join([char for char in cheque_issue.issue_cheque_date.strftime('%d%m%Y')]),
        'payee': formatted_payee_name,
        'amount': '*' + '*' + str(issue_amount) + '*' + '*',
        'amount_word': formatted_amount_word,
        'positions': {
            'date': (cheque_text.date_x_position, cheque_text.date_y_position, cheque_text.date_font, cheque_text.date_size, cheque_text.date_bold, cheque_text.date_italic),
            'payee': (cheque_text.payee_x_position, cheque_text.payee_y_position, cheque_text.payee_font, cheque_text.payee_size, cheque_text.payee_bold, cheque_text.payee_italic),
            'amount_word': (cheque_text.amtwrds_x_position, cheque_text.amtwrds_y_position, cheque_text.amtwrds_font, cheque_text.amtwrds_size, cheque_text.amtwrds_bold, cheque_text.amtwrds_italic),
            'amount_num': (cheque_text.amtnum_x_position, cheque_text.amtnum_y_position, cheque_text.amtnum_font, cheque_text.amtnum_size, cheque_text.amtnum_bold, cheque_text.amtnum_italic),
            'sign': (cheque_text.sign_x_position, cheque_text.sign_y_position),
        },
        'sign_url': sign_url,
        'cheque_id': cheque_id,
        'issue_currency':issue_currency,
        
        }
    return render(request, 'Cheque_issue/print_cheque.html', context)


@login_required
def approval(request, cheque_id):

    additional_value = request.GET.get('additional_value')

    print("add val - ", additional_value)

    cheque_issue = get_object_or_404(ChequeIssue, id=cheque_id)
    if cheque_issue.issue_is_approved is None and additional_value == "True":
        cheque_issue.issue_is_approved = True
        cheque_issue.issue_approv_rejectby = request.user.id
        cheque_issue.modified_by = request.user.id
        cheque_issue.modified_date = datetime.now()
        messages.success(request, f'Cheque to {cheque_issue.issue_payee.payee_name} of Cheque Number - {cheque_issue.issue_cheque_no} is Approved.')
    
    elif cheque_issue.issue_is_approved is None and additional_value == "False":
        cheque_issue.issue_is_approved = False
        cheque_issue.issue_approv_rejectby = request.user.id
        cheque_issue.modified_by = request.user.id
        cheque_issue.modified_date = datetime.now()
        messages.success(request, f'Cheque to {cheque_issue.issue_payee.payee_name} of Cheque Number - {cheque_issue.issue_cheque_no} is Rejected.')
    
    elif cheque_issue.issue_is_approved == False:
        cheque_issue.issue_is_approved = True
        cheque_issue.issue_approv_rejectby = request.user.id
        cheque_issue.modified_by = request.user.id
        cheque_issue.modified_date = datetime.now()
        messages.success(request, f'Rejected Cheque to {cheque_issue.issue_payee.payee_name} of Cheque Number - {cheque_issue.issue_cheque_no} is Approved.')
    
    elif cheque_issue.issue_is_approved == True:
        cheque_issue.issue_is_approved = False
        cheque_issue.issue_approv_rejectby = request.user.id
        cheque_issue.modified_by = request.user.id
        cheque_issue.modified_date = datetime.now()
        messages.error(request, f'Approved Cheque to {cheque_issue.issue_payee.payee_name} of Cheque Number - {cheque_issue.issue_cheque_no} is Rejected.')

    cheque_issue.save()

    previous_url = request.META.get('HTTP_REFERER')

    return redirect(previous_url)



    
    
