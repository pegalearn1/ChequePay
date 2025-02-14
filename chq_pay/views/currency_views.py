''' The Project 'Cheque Printer' is solely created by Faraz Ahmed Raj - Python Developer
in 2024-2025.'''

from .imp_libs import *
from chq_pay.models import Currencies, Company_Setup, ChequeTemplate

@login_required
def add_currency(request):
    if request.method == "POST":
        currency_char = request.POST.get("currency_char")
        currency_name = request.POST.get("currency_name")
        
        currency_exist = Currencies.objects.filter(Q(currency_name=currency_name) | Q(currency_char=currency_char))

        if currency_exist:
            messages.warning(request,('Currency Already Exits!!'))
        else:
            # Save to the database
            currency = Currencies.objects.create(
                currency_char=currency_char,
                currency_name=currency_name,
                created_by = request.user.id,
                created_date = datetime.now(),
                modified_by = request.user.id,
                modified_date = datetime.now()

            )
            messages.success(request,('Currency Created Successfully!!!'))
            return JsonResponse({"success": True})
    return JsonResponse({"success": False})


@login_required
def currency_list(request):
    currencies = Currencies.objects.all().order_by('currency_char')

    #pagination
    per_page = 25
    paginator = Paginator(currencies, per_page)
    page_number = request.GET.get('page')
    currency_list = paginator.get_page(page_number)
    #pagination

    return render(request,"Currency/currency_list_new.html",{'currencies':currency_list})


@login_required
def delete_currency(request, currency_id):
    
    currency_exist = ChequeTemplate.objects.filter(currency = currency_id).exists()

    if not currency_exist:
        currency = get_object_or_404(Currencies, id=currency_id)
        currency.delete()
        messages.success(request,('Currency Deleted Successfully!!!'))
        return redirect('currency_list')
    else:
        messages.error(request,('Cannot delete this currency, a template exists with this currency.!!'))
        return redirect('currency_list')


@login_required
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
                messages.warning(request,('Currency with same name or Currency Char already exits!!'))

            else:
                currency.save()
                messages.success(request,('Currency Details Updated Successfully!!!'))
                return JsonResponse({"success": True})
        except Currencies.DoesNotExist:
            return JsonResponse({"success": False, "error": "Currency not found"})
    return JsonResponse({"success": False, "error": "Invalid request"})