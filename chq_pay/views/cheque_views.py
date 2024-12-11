''' The Project 'Cheque Printer' is solely created by Faraz Ahmed Raj - Python Developer
in 2024-2025.'''

from .imp_libs import *
from chq_pay.forms import ChequeTemplateForm, ChequeTextForm
from chq_pay.models import ChequeTemplate, ChequeText

def upload_template(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        width = request.POST.get('width')
        height = request.POST.get('height')
        background_image = request.FILES.get('background_image')


        # Save the data to the database
        if name and width and height and background_image:
            cheque_template = ChequeTemplate(
                name=name,
                width=width,
                height=height,
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
    return JsonResponse({"success": False})

def template_list(request):
    templates = ChequeTemplate.objects.all()
    return render(request, 'Cheque_templates/template_list.html', {'templates': templates})

def delete_template(request, template_id):
    template = get_object_or_404(ChequeTemplate, id=template_id)
    template.delete()
    messages.error(request,('Template Deleted Successfully!!'))
    return redirect('template_list')


def edit_template(request):
    if request.method == "POST":
        template_id = request.POST.get("template_id")
        name = request.POST.get('name')
        width = request.POST.get('width')
        height = request.POST.get('height')
        background_image = request.FILES.get('background_image')

        print("currency_id - ",template_id)
        
        # Update the bank in the database
        try:
            template = ChequeTemplate.objects.get(id=template_id)
            template.name = name
            template.width = width
            template.height = height
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


def template_detail(request, template_id):
    template = get_object_or_404(ChequeTemplate, id=template_id)
    texts = ChequeText.objects.filter(template=template)
    return render(request, 'Cheque_templates/template_detail.html', {'template': template, 'texts': texts})


def add_text_to_template(request, template_id):
    template = get_object_or_404(ChequeTemplate, id=template_id)
    previous_texts = ChequeText.objects.filter(template=template)
    if request.method == 'POST':
        # Extract data from POST request
        text = request.POST.get('text')
        x_position = request.POST.get('x_position', '0')  # Default to '0' if empty
        y_position = request.POST.get('y_position', '0')  # Default to '0' if empty

        # Validate required fields
        if not text:
            return HttpResponseBadRequest("Text is required.")

        # Convert positions to float, default to 0 if conversion fails
        # try:
        #     x_position = float(x_position)
        #     y_position = float(y_position)
        # except ValueError:
        #     x_position = 0.0
        #     y_position = 0.0

        # Save the data to the model
        cheque_text = ChequeText.objects.create(
            template=template,
            text=text,
            x_position=x_position,
            y_position=y_position,
            created_by = request.user.id,
            created_date = datetime.now(),
            modified_by = request.user.id,
            modified_date = datetime.now()

        )

        return HttpResponseRedirect(request.path)

    return render(request, 'Cheque_templates/add_text.html', {'template': template, 'previous_texts':previous_texts})


def delete_text(request, text_id, temp_id):
    text = get_object_or_404(ChequeText, id=text_id)
    text.delete()
    messages.warning(request, f"Text attribute-{text} template deleted.")
    print(f"template id = {temp_id}")
    return redirect('template_detail',temp_id)



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