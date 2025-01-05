''' The Project 'Cheque Printer' is solely created by Faraz Ahmed Raj - Python Developer
in 2024-2025.'''

from .imp_libs import *
from chq_pay.models import Banks

@login_required
def add_bank(request):
    if request.method == "POST":
        bank_char = request.POST.get("bank_char")
        bank_name_e = request.POST.get("bank_name_e")
        bank_name_l = request.POST.get("bank_name_l")
        tel_no = request.POST.get("tel_no")
        address = request.POST.get("address")

        bank_exist = Banks.objects.filter(Q(bank_name_e=bank_name_e) | Q(bank_char=bank_char))

        if bank_exist:
            messages.error(request,('Bank Already Exits!!'))
        else:
            # Save to the database
            bank = Banks.objects.create(
                bank_char=bank_char,
                bank_name_e=bank_name_e,
                bank_name_l=bank_name_l,
                tel_no=tel_no,
                address=address,
                created_by = request.user.id,
                created_date = datetime.now(),
                modified_by = request.user.id,
                modified_date = datetime.now()

            )
            messages.success(request,('Bank Created Successfully!!!'))
            return JsonResponse({"success": True})
    return JsonResponse({"success": False})

@login_required
def bank_list(request):
    banks = Banks.objects.all().order_by('bank_char')

    #pagination
    per_page = 25
    paginator = Paginator(banks, per_page)
    page_number = request.GET.get('page')
    banks_list = paginator.get_page(page_number)
    #pagination

    return render(request,"Banks/bank_list_new.html",{'banks':banks_list})

@login_required
def delete_bank(request, bank_id):
    bank = get_object_or_404(Banks, id=bank_id)
    bank.delete()
    messages.error(request,('Bank Deleted Successfully!!!'))
    return redirect('bank_list')

@login_required
def edit_bank(request):
    if request.method == "POST":
        bank_id = request.POST.get("bank_id")
        bank_char = request.POST.get("bank_char")
        bank_name_e = request.POST.get("bank_name_e")
        bank_name_l = request.POST.get("bank_name_l")
        tel_no = request.POST.get("tel_no")
        address = request.POST.get("address")
        print("bccbcbcbcb = ",bank_char)
        
        # Update the bank in the database
        try:
            bank = Banks.objects.get(id=bank_id)
            bank.bank_char = bank_char
            bank.bank_name_e = bank_name_e
            bank.bank_name_l = bank_name_l
            bank.tel_no = tel_no
            bank.address = address
            bank.modified_by = request.user.id
            bank.modified_date = datetime.now()

            bank_exist = Banks.objects.filter(Q(bank_name_e=bank_name_e) | Q(bank_char=bank_char)).exclude(id=bank_id)

            if bank_exist:
                messages.error(request,('Bank with same name or bank char already exits!!'))

            else:
                
                bank.save()
                messages.success(request,('Bank Details Updated Successfully!!!'))
                return JsonResponse({"success": True})
        except Banks.DoesNotExist:
            return JsonResponse({"success": False, "error": "Bank not found"})
    return JsonResponse({"success": False, "error": "Invalid request"})