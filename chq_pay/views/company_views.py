''' The Project 'Cheque Printer' is solely created by Faraz Ahmed Raj - Python Developer
in 2024-2025.'''

from .imp_libs import *
from chq_pay.models import Company_Setup, Currencies


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
                currency_id=currency_id,
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




def delete_currency(request, currency_id):
    currency = get_object_or_404(Currencies, id=currency_id)
    currency.delete()
    messages.error(request,('Currency Deleted Successfully!!!'))
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