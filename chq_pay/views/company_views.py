''' The Project 'Cheque Printer' is solely created by Faraz Ahmed Raj - Python Developer
in 2024-2025.'''

from .imp_libs import *
from chq_pay.models import Company_Setup, Currencies, Banks, ChequeTemplate, ChequeIssue


def add_company(request):
    if request.method == "POST":
        registration_id = request.POST.get("company_registration_id")
        company_name = request.POST.get("company_name")
        logo = request.POST.get("company_logo")
        tax_id = request.POST.get("company_tax_id")
        currency_id = request.POST.get("company_currency_id")
        tel_no = request.POST.get("company_tel_no")
        email = request.POST.get("company_email")
        address = request.POST.get("company_address")
        
        
        company_exist = Company_Setup.objects.filter(company_name=company_name)

        if company_exist:
            messages.error(request,('Company Already Exits!!'))
        else:
            # Save to the database
            company_name = Company_Setup.objects.create(
                registration_id=registration_id,
                company_name=company_name,
                tax_id=tax_id,
                tel_no=tel_no,
                email=email,
                address=address,
                created_by = request.user.id,
                created_date = datetime.now(),
                modified_by = request.user.id,
                modified_date = datetime.now()

            )
            messages.success(request,('Company Created Successfully!!!'))
            return JsonResponse({"success": True})
    return JsonResponse({"success": False})



@login_required
def company_list(request):
    companies = Company_Setup.objects.all().order_by('company_name')

    #pagination
    per_page = 25
    paginator = Paginator(companies, per_page)
    page_number = request.GET.get('page')
    company_list = paginator.get_page(page_number)
    #pagination

    return render(request,"Companies/company_list.html",{'companies':company_list})




def delete_company(request, company_id):
    company = get_object_or_404(Company_Setup, id=company_id)
     # Check if the company ID exists in other models
    related_models = [
        Banks,  
        ChequeTemplate,
        ChequeIssue
    ]
    
    for model in related_models:
        if model.objects.filter(company_id=company_id).exists():
            messages.error(request, 'Cannot delete the company as it is referenced in other records.')
            return redirect('currency_list')
    
    # If no references exist, delete the company
    company.delete()
    messages.error(request,('Company Deleted Successfully!!!'))
    return redirect('currency_list')

def edit_currency(request):
    if request.method == "POST":
        currency_id = request.POST.get("currency_id")
        currency_char = request.POST.get("currency_char")
        currency_name = request.POST.get("currency_name")

        print("currency_id - ",currency_id)
        
        # Update the bank in the database
        try:
            currency = Currencies.objects.get(id=currency_id)
            currency.currency_char = currency_char
            currency.currency_name = currency_name
            currency.modified_by = request.user.id
            currency.modified_date = datetime.now()

            currency_exist = Currencies.objects.filter(Q(currency_name=currency_name) | Q(currency_char=currency_char)).exclude(id=currency_id)

            if currency_exist:
                messages.error(request,('Currency with same name or Currency Char already exits!!'))

            else:
                
                currency.save()
                messages.success(request,('Currency Details Updated Successfully!!!'))
                return JsonResponse({"success": True})
        except Currencies.DoesNotExist:
            return JsonResponse({"success": False, "error": "Currency not found"})
    return JsonResponse({"success": False, "error": "Invalid request"})

@csrf_exempt
def current_company(request):
    if request.method == 'POST':
        company_id = request.POST.get("current_company")

        if company_id:
            # Reset all companies to is_selected = False
            Company_Setup.objects.update(is_selected=False)

            # Set the selected company to is_selected = True
            selected_company = get_object_or_404(Company_Setup, id=company_id)
            selected_company.is_selected = True
            selected_company.save()
            messages.success(request,(f'Company Switched To {selected_company.company_name}'))
            previous_path = request.META.get('HTTP_REFERER', '/')
            return redirect(previous_path)
        else:

            messages.error(request,("Company Doesn't Exists."))


    else:
        return redirect('index')

    

    return HttpResponse('Company Switched')
