''' The Project 'Cheque Printer' is solely created by Faraz Ahmed Raj - Python Developer
in 2024-2025.'''

from .imp_libs import *
from chq_pay.models import ChequeTemplate, ChequeText, Banks, Currencies, Payee, ChequeIssue, Company_Setup, AppUser

@login_required
def upload_template(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        width = request.POST.get('width')
        height = request.POST.get('height')
        bank = request.POST.get('bank')
        currency = request.POST.get('currency')
        background_image = request.FILES.get('background_image')

        print("POST - ", request.POST)

        comapny_now = get_object_or_404(Company_Setup, is_selected = True)


        # Save the data to the database
        if name and width and height and background_image:
            try:
                cheque_template = ChequeTemplate(
                    company = comapny_now,
                    name=name,
                    width=width,
                    height=height,
                    bank = get_object_or_404(Banks, id = bank),
                    currency = get_object_or_404(Currencies, id = currency),
                    background_image=background_image,
                    created_by = request.user.id,
                    created_date = datetime.now(),
                    modified_by = request.user.id,
                    modified_date = datetime.now()

                )

                template_exist = ChequeTemplate.objects.filter(name=name)
                allowed_temp_count = AppUser.objects.values('allowed_templates')[0]['allowed_templates']
                temp_count = ChequeTemplate.objects.count()

                if template_exist:
                    messages.warning(request,('Template Already Exits!!'))
                else:
                    if temp_count >= allowed_temp_count:
                        messages.error(request,('Template limit reached,please upgrade license to continue.'))
                    else:
                        cheque_template.save()
                        messages.success(request,('Template Created Successfully!!!'))
                        return JsonResponse({"success": True})
                    
            except Exception as e:
                print("error : ",str(e))
    return JsonResponse({"success": False})



@login_required
def template_list(request):
    templates = ChequeTemplate.objects.all().filter(Q(company__is_selected=True)).order_by('name')
    banks = Banks.objects.all()
    currencies = Currencies.objects.all()
    

    # Filter by search term if provided
    search = request.GET.get('search', '')
    if search:
        templates = templates.filter(Q(name__icontains=search)|Q(currency__currency_char=search)|Q(bank__bank_name_e=search))

    # Fetch filter parameters
    selected_bank = request.GET.get('bank')
    selected_currency = request.GET.get('currency')

   
    # Apply filters if provided
    if selected_bank:
        templates = templates.filter(bank__bank_name_e=selected_bank)
    if selected_currency:
        templates = templates.filter(currency__currency_char=selected_currency)
    
    #pagination
    per_page = 25
    paginator = Paginator(templates, per_page)
    page_number = request.GET.get('page')
    temp_list = paginator.get_page(page_number)
    #pagination

    context = {'templates': temp_list,
               'banks':banks,
               'currencies':currencies,
              
               }
    return render(request, 'Cheque_templates/template_list.html', context )


@login_required
def delete_template(request, template_id):
    issued_templ = ChequeIssue.objects.filter(issue_template = template_id).exists()
    cheque_txt = ChequeText.objects.filter(template = template_id)
    template = get_object_or_404(ChequeTemplate, id=template_id)
    
    if issued_templ:
        messages.error(request,("Can't be deleted, Cheque has been issued with the template"))
    else:
        if cheque_txt:
            cheque_txt.delete()
        template.delete()
        messages.success(request,('Template Deleted Successfully!!'))
    return redirect('template_list')


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

        print("image - ",background_image)

        print("currency_id - ",template_id)
        
        # Update the bank in the database
        try:
            template = ChequeTemplate.objects.get(id=template_id)
            template.name = name
            template.width = width
            template.height = height
            template.bank = get_object_or_404(Banks, id=bank)
            template.modified_by = request.user.id
            template.modified_date = datetime.now()

            if background_image:
                if ChequeIssue.objects.filter(issue_template=template).exists():
                    # If a cheque is already issued, prevent updating the background image
                    messages.warning(request, "Template can't be updated after a cheque has been issued.")
                else:
                    # No cheques have been issued, allow updating the background image
                    template.background_image = background_image

            if currency:
                if ChequeIssue.objects.filter(issue_template=template).exists():
                    # Check if the currency is the same as the existing one
                    if template.currency.id != int(currency):
                        messages.warning(request, "Currency can't be edited after a cheque has been issued.")
                    else:
                        # No change in currency; update the template currency
                        template.currency = get_object_or_404(Currencies, id=currency)
                else:
                    # No cheques have been issued; update the currency
                    template.currency = get_object_or_404(Currencies, id=currency)
                    



            template_exist = ChequeTemplate.objects.filter(name=name).exclude(id=template_id)

            if template_exist:
                messages.warning(request,('Template with same name already exits!!'))

            else:
                template.save()
                messages.success(request,('Template Details Updated Successfully!!!'))
                return JsonResponse({"success": True})
        except ChequeTemplate.DoesNotExist:
            return JsonResponse({"success": False, "error": "Currency not found"})
    return JsonResponse({"success": False, "error": "Invalid request"})


@login_required
def template_detail(request, template_id):
    template = get_object_or_404(ChequeTemplate, id=template_id)
    chq_txts = ChequeText.objects.filter(template=template)

    template_height =  template.height
    template_width =  template.width
    template_background = template.background_image.url

    print(template_background)

    context = {

        'chq_txts':chq_txts,
        'template':template,


    }
    
    return render(request, 'Cheque_templates/template_detail.html', context)



@login_required
def add_text_to_template(request, template_id):
    template = get_object_or_404(ChequeTemplate, id=template_id)

    text_fields = [
        'date_x_position', 'date_y_position', 'payee_x_position', 'payee_y_position',
        'amtwrds_x_position', 'amtwrds_y_position', 'amtnum_x_position', 'amtnum_y_position',
        'sign_x_position', 'sign_y_position'
    ]
    
    if request.method == 'POST':
        # Prepare the dictionary for updating or creating
        valid_data = {}

        for tf in text_fields:
            value = request.POST.get(tf)

            # Only add the field to valid_data if the value is not None, empty, or invalid (like '0')
            if value not in [None, '', '0']:
                try:
                    valid_data[tf] = float(value)  # Convert the value to float
                except ValueError:
                    pass  # Ignore invalid values that cannot be converted to float

        if valid_data:  # Proceed only if there is valid data
            valid_data.update({
                'created_by': request.user.id,
                'created_date': datetime.now(),
                'modified_by': request.user.id,
                'modified_date': datetime.now(),
            })

            # Update or create the text object
            ChequeText.objects.update_or_create(
                template=template,
                defaults=valid_data
            )
            messages.success(request, 'Text position is set.')
        else:
            messages.warning(request, 'No valid positions provided.')

        return redirect('template_detail', template_id)

    # If GET request, retrieve existing data
    text = ChequeText.objects.filter(template=template).first()
    return render(request, 'Cheque_templates/add_text.html', {'template': template, 'text': text})





@login_required
def delete_text(request, text_id, temp_id):
    if ChequeIssue.objects.filter(issue_template=temp_id).exists():
        messages.warning(request, "Cheque issued, text can't be deleted")
    else:
        text = get_object_or_404(ChequeText, id=text_id)
        if text:
            text_atrrb = request.GET.get('text_atrrb')

            print("texttt - ", text_atrrb)
            
            if text_atrrb =='Date':
                text.date_x_position = None
                text.date_y_position = None
            
            elif text_atrrb =='Payee':
                text.payee_x_position = None
                text.payee_y_position = None
            
            elif text_atrrb =='Amt_Wrds':
                text.amtwrds_x_position = None
                text.amtwrds_y_position = None
            
            elif text_atrrb =='Amt_Num':
                text.amtnum_x_position = None
                text.amtnum_y_position = None
            
            elif text_atrrb == 'Sign':
                text.sign_x_position = None
                text.sign_y_position = None

            text.save()
            messages.success(request, f"Text attribute deleted.")
    return redirect('template_detail',temp_id)



@login_required
def print_cheque(request, template_id):
    template = get_object_or_404(ChequeTemplate, id=template_id)
    texts = ChequeText.objects.filter(template=template)

    # Load the cheque template with texts into an HTML file for printing
    html_template = get_template('print_cheque.html')
    html_content = html_template.render({'template': template, 'texts': texts})

    # Save the generated HTML content to a file for printing
    html_file_path = os.path.join(settings.BASE_DIR, 'printed_cheques','cheque_print.html')
    with open(html_file_path, 'w') as f:
        f.write(html_content)

    # Use a browser to print the HTML file (Chrome example)
    # Ensure Chrome is installed and added to the PATH
    print_command = f'start chrome --headless --print-to-pdf --no-margins --print-to-pdf-no-header "{html_file_path}"'
    subprocess.run(print_command, shell=True)

    return HttpResponse("Cheque sent to printer!")