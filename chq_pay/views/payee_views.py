''' The Project 'Cheque Printer' is solely created by Faraz Ahmed Raj - Python Developer
in 2024-2025.'''

from .imp_libs import *
from chq_pay.models import Payee, Company_Setup


@login_required
def add_payee(request):
    if request.method == "POST":
        payee_name = request.POST.get("payee_name")
        mobile_no = request.POST.get("payee_mobile_no")
        email = request.POST.get("payee_email")
        
        payee_exist = Payee.objects.filter(payee_name = payee_name)

        
        if payee_exist:
            messages.error(request,('Payee Already Exits!!'))

        else:
            # Save to the database
            payee = Payee.objects.create(
                payee_name=payee_name,
                mobile_no=mobile_no,
                email=email,
                created_by = request.user.id,
                created_date = datetime.now(),
                modified_by = request.user.id,
                modified_date = datetime.now()

            )
            messages.success(request,('Payee Created Successfully!!!'))
            return JsonResponse({"success": True})
    return JsonResponse({"success": False})


@login_required
def payee_list(request):
    payees = Payee.objects.all().order_by('payee_name')

    #pagination
    per_page = 25
    paginator = Paginator(payees, per_page)
    page_number = request.GET.get('page')
    payee_list = paginator.get_page(page_number)
    #pagination

    return render(request,"Payees/payee_list_new.html",{'payees':payee_list})


@login_required
def delete_payee(request, payee_id):
    payee = get_object_or_404(Payee, id=payee_id)
    payee.delete()
    messages.error(request,('Payee Deleted Successfully!!!'))
    return redirect('payee_list')


@login_required
def edit_payee(request):
    if request.method == "POST":
        payee_id = request.POST.get("payee_id")
        payee_name = request.POST.get("payee_name")
        mobile_no = request.POST.get("payee_mobile_no")
        email = request.POST.get("payee_email")
        print("payeee = ",payee_id)
        
        # Update the bank in the database
        try:
            payee = Payee.objects.get(id=payee_id)
            payee.payee_name = payee_name
            payee.mobile_no = mobile_no
            payee.email = email
            payee.modified_by = request.user.id
            payee.modified_date = datetime.now()
            
            payee_exist = Payee.objects.filter(payee_name = payee_name).exclude(id=payee_id)

            if payee_exist:
                messages.error(request,('Payee with the name already exits!!'))

            else:
                payee.save()
                messages.success(request,('Payee Details Updated Successfully!!!'))
                return JsonResponse({"success": True})
        except Payee.DoesNotExist:
            return JsonResponse({"success": False, "error": "Payee not found"})
    return JsonResponse({"success": False, "error": "Invalid request"})