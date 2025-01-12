''' The Project 'Cheque Printer' is solely created by Faraz Ahmed Raj - Python Developer
in 2024-2025.'''

from .imp_libs import *
from chq_pay.models import Company_Setup, Currencies, Banks, ChequeTemplate, ChequeIssue, AppUser


def add_company(request):
    if request.method == "POST":
        company_name = request.POST.get("company_name")
        tel_no = request.POST.get("company_tel_no")
        email = request.POST.get("company_email")
        tax_id = request.POST.get("company_tax_id")
        address = request.POST.get("company_address")
        logo = request.FILES.get("company_logo")
        
        company_exist = Company_Setup.objects.filter(company_name=company_name).exists()

        reg_code = AppUser.objects.values_list('reg_code', flat=True).first()

        print("reg code - ", reg_code)

        if company_exist:
            messages.error(request,('Company Already Exits!!'))
        else:
            # Save to the database
            try:
                company = Company_Setup(
                    registration_id = reg_code,
                    company_name=company_name,
                    tax_id=tax_id,
                    tel_no=tel_no,
                    email=email,
                    address=address,
                    is_selected = False,
                    created_by = request.user.id,
                    created_date = datetime.now(),
                    modified_by = request.user.id,
                    modified_date = datetime.now()
                )

                if logo:
                    company.logo = logo

                company.save()
                    
                messages.success(request,('Company Created Successfully!!!'))
                return JsonResponse({"success": True})
            except Exception as e:
                print("Company adding error - ",str(e))
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
        ChequeTemplate,
        ChequeIssue
    ]
    
    for model in related_models:
        if model.objects.filter(company=company).exists():
            messages.error(request, 'Cannot delete the company as it is referenced in other records.')
            return redirect('company_list')
    
    # If no references exist, delete the company
    company.delete()
    messages.error(request,('Company Deleted Successfully!!!'))
    return redirect('company_list')

def edit_company(request):
    if request.method == "POST":
        company_id = request.POST.get("company_id")
        company_name = request.POST.get("company_name")
        tel_no = request.POST.get("company_tel_no")
        email = request.POST.get("company_email")
        tax_id = request.POST.get("company_tax_id")
        address = request.POST.get("company_address")
        logo = request.FILES.get("company_logo")


        company_exist = Company_Setup.objects.filter(company_name=company_name).exclude(id=company_id).exists()

        reg_code = AppUser.objects.values_list('reg_code', flat=True).first()

        print("reg code - ", reg_code)

        if company_exist:
            messages.error(request,('Company Already Exits!!'))
        else:
            # Save to the database
            try:
                company = get_object_or_404(Company_Setup, id = company_id)

                company.registration_id = reg_code
                company.company_name=company_name
                company.tax_id=tax_id
                company.tel_no=tel_no
                company.email=email
                company.address=address
                company.modified_by = request.user.id
                company.modified_date = datetime.now()
                

                if logo:
                    company.logo = logo

                company.save()
                messages.success(request,('Company Details Updated Successfully!!!'))
                return JsonResponse({"success": True})
            except Company_Setup.DoesNotExist:
                return JsonResponse({"success": False, "error": "Company not found"})
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
