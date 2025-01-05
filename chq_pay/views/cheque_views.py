''' The Project 'Cheque Printer' is solely created by Faraz Ahmed Raj - Python Developer
in 2024-2025.'''

from .imp_libs import *
from chq_pay.models import ChequeTemplate, ChequeText, Banks, Currencies, Payee

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


        # Save the data to the database
        if name and width and height and background_image:
            try:
                cheque_template = ChequeTemplate(
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

                if template_exist:
                    messages.error(request,('Template Already Exits!!'))
                else:
                    cheque_template.save()
                    messages.success(request,('Template Created Successfully!!!'))
                    
                    response = ({"success": True})
                    print("responseee = ",response)
                    return JsonResponse(response)
            except Exception as e:
                print("error : ",str(e))
    return JsonResponse({"success": False})


@login_required
def template_list(request):
    templates = ChequeTemplate.objects.all().order_by('name')
    banks = Banks.objects.all()
    currencies = Currencies.objects.all()

    #pagination
    per_page = 25
    paginator = Paginator(templates, per_page)
    page_number = request.GET.get('page')
    temp_list = paginator.get_page(page_number)
    #pagination

    context = {'templates': temp_list,
               'banks':banks,
               'currencies':currencies}
    return render(request, 'Cheque_templates/template_list.html', context )


@login_required
def delete_template(request, template_id):
    template = get_object_or_404(ChequeTemplate, id=template_id)
    template.delete()
    messages.error(request,('Template Deleted Successfully!!'))
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
def template_detail(request, template_id):
    template = get_object_or_404(ChequeTemplate, id=template_id)
    chq_txts = ChequeText.objects.filter(template=template)
    
    return render(request, 'Cheque_templates/template_detail.html', {'template': template, 'chq_txts': chq_txts})



@login_required
def add_text_to_template(request, template_id):
    template = get_object_or_404(ChequeTemplate, id=template_id)
    
    if request.method == 'POST':
        ChequeText.objects.update_or_create(
            template=template,
            defaults={
                'date_x_position': request.POST.get('date_x_position', '0'),
                'date_y_position': request.POST.get('date_y_position', '0'),
                'payee_x_position': request.POST.get('payee_x_position', '0'),
                'payee_y_position': request.POST.get('payee_y_position', '0'),
                'amtwrds_x_position': request.POST.get('amtwrds_x_position', '0'),
                'amtwrds_y_position': request.POST.get('amtwrds_y_position', '0'),
                'amtnum_x_position': request.POST.get('amtnum_x_position', '0'),
                'amtnum_y_position': request.POST.get('amtnum_y_position', '0'),
                'sign_x_position': request.POST.get('sign_x_position', '0'),
                'sign_y_position': request.POST.get('sign_y_position', '0'),
                'created_by': request.user.id,
                'created_date': datetime.now(),
                'modified_by': request.user.id,
                'modified_date': datetime.now(),
                
            }
        )
        messages.success(request,('Text position is set.'))
        return redirect('template_detail',template_id)

    text = ChequeText.objects.filter(template=template).first()
    return render(request, 'Cheque_templates/add_text.html', {'template': template, 'text': text})



@login_required
def delete_text(request, text_id, temp_id):
    text = get_object_or_404(ChequeText, id=text_id)
    text.delete()
    messages.warning(request, f"Text attribute-{text} template deleted.")
    print(f"template id = {temp_id}")
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