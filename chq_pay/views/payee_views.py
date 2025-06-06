''' The Project 'Cheque Printer' is solely created by Faraz Ahmed Raj - Python Developer
in 2024-2025.'''

from .imp_libs import *
from django.utils.crypto import get_random_string
from chq_pay.models import Payee, Company_Setup, ChequeIssue, TempDatas, Banks


from django.db import IntegrityError

@login_required
def add_payee(request):
    if request.method == "POST":
        try:
            payee_name = request.POST.get("payee_name")
            payee_bank = request.POST.get("payee_bank")
            payee_acc_no = request.POST.get("payee_acc_no")
            mobile_no = request.POST.get("payee_mobile_no")
            email = request.POST.get("payee_email")
            address = request.POST.get("payee_address")

            # Clean and convert
            payee_acc_no = int(payee_acc_no) if payee_acc_no else None

            acc_no_exists = (
                Payee.objects.filter(payee_acc_no=payee_acc_no).exists()
                if payee_acc_no is not None else False
            )
            mobile_exists = (
                Payee.objects.filter(mobile_no=mobile_no).exists()
                if mobile_no else False
            )

            if acc_no_exists or mobile_exists:
                messages.warning(
                    request,
                    'Payee with same account number or mobile number already exists!!'
                )
                return JsonResponse({"success": False})

            # Create payee
            payee = Payee.objects.create(
                payee_name=payee_name.title(),
                payee_acc_no=payee_acc_no,
                mobile_no=mobile_no,
                email=email,
                address=address if address else None,
                payee_bank=get_object_or_404(Banks, id=payee_bank) if payee_bank else None,
                created_by=request.user.id,
                created_date=datetime.now(),
                modified_by=request.user.id,
                modified_date=datetime.now()
            )

            messages.success(request, 'Payee Created Successfully!!!')
            return JsonResponse({"success": True})

        except ValueError:
            return JsonResponse({"success": False, "error": "Invalid account number. Must be numeric."})
        except IntegrityError as e:
            return JsonResponse({"success": False, "error": f"Database error: {str(e)}"})
        except Exception as e:
            return JsonResponse({"success": False, "error": f"Unexpected error: {str(e)}"})

    return JsonResponse({"success": False, "error": "Invalid request method"})



@login_required
def payee_list(request):
    payees = Payee.objects.all().order_by('payee_name')
    banks = Banks.objects.all()

    #pagination
    per_page = 25
    paginator = Paginator(payees, per_page)
    page_number = request.GET.get('page')
    payee_list = paginator.get_page(page_number)
    #pagination

    return render(request,"Payees/payee_list_new.html",{'payees':payee_list, 'banks':banks})


@login_required
def delete_payee(request, payee_id):
    payee_exists = ChequeIssue.objects.filter(issue_payee = payee_id).exists()

    if not payee_exists:
        payee = get_object_or_404(Payee, id=payee_id)
        payee.delete()
        messages.success(request,('Payee Deleted Successfully!!!'))
        return redirect('payee_list')
    else:
        messages.error(request,('Cannot delete as a cheque has been already issued for the payee. '))
        return redirect('payee_list')


@login_required
def edit_payee(request):
    if request.method == "POST":
        payee_id = request.POST.get("payee_id")
        payee_name = request.POST.get("payee_name")
        payee_bank = request.POST.get("payee_bank")
        payee_acc_no_raw = request.POST.get("payee_acc_no")
        payee_acc_no = int(payee_acc_no_raw) if payee_acc_no_raw else None
        mobile_no = request.POST.get("payee_mobile_no")
        email = request.POST.get("payee_email")
        address = request.POST.get("payee_address")

        try:
            payee = Payee.objects.get(id=payee_id)
            cheque_issued = ChequeIssue.objects.filter(issue_payee=payee_id).exists()

            # Uniqueness checks
            acc_no_exists = (
                Payee.objects.filter(payee_acc_no=payee_acc_no)
                .exclude(id=payee_id)
                .exists()
                if payee_acc_no is not None else False
            )
            mobile_exists = (
                Payee.objects.filter(mobile_no=mobile_no)
                .exclude(id=payee_id)
                .exists()
                if mobile_no else False
            )

            if acc_no_exists or mobile_exists:
                messages.warning(request, "Payee with same account number or mobile number already exists!!")
                return JsonResponse({"success": False})

            if cheque_issued:
                # Only restrict editing of payee_name
                payee.mobile_no = mobile_no
                payee.email = email
                payee.payee_acc_no = payee_acc_no if payee_acc_no else None

                if payee_bank:
                    payee.payee_bank = get_object_or_404(Banks, id=payee_bank)
                if address:
                    payee.address = address

                payee.modified_by = request.user.id
                payee.modified_date = datetime.now()

                payee.save()
                messages.success(request, "Payee updated (name not editable due to issued cheque).")
                return JsonResponse({"success": True})

            else:
                # Full update allowed
                payee.payee_name = payee_name.title()
                payee.mobile_no = mobile_no
                payee.email = email
                payee.payee_acc_no = payee_acc_no if payee_acc_no else None

                if payee_bank:
                    payee.payee_bank = get_object_or_404(Banks, id=payee_bank)
                if address:
                    payee.address = address

                payee.modified_by = request.user.id
                payee.modified_date = datetime.now()

                payee.save()
                messages.success(request, "Payee Details Updated Successfully!!!")
                return JsonResponse({"success": True})

        except Payee.DoesNotExist:
            return JsonResponse({"success": False, "error": "Payee not found"})
        except Exception as e:
            print(f"Error updating payee: {str(e)}")
            return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse({"success": False, "error": "Invalid request"})





@csrf_exempt
@login_required
def validate_excel_payee(request):
    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES['file']
        try:
            # Load the Excel file
            df = pd.read_excel(file)

            # Ensure the headers match the expected column names
            expected_columns = ['PAYEE NAME*', 'MOBILE NUMBER', 'EMAIL', 'ADDRESS']
            if list(df.columns) != expected_columns:
                return JsonResponse({
                    'error': 'Invalid file format. Ensure the headers are: {}'.format(", ".join(expected_columns))
                }, status=400)

            results = []
            valid_rows = []
            seen_mobiles = set()

            # Iterate through rows to validate data
            for _, row in df.iterrows():
                try:
                    payee_name = str(row['PAYEE NAME*']).strip() if not pd.isna(row['PAYEE NAME*']) else ""
                    mobile_no = str(row['MOBILE NUMBER']).strip() if not pd.isna(row['MOBILE NUMBER']) else ""
                    email = str(row['EMAIL']).strip() if not pd.isna(row['EMAIL']) else ""
                    address = str(row['ADDRESS']).strip() if not pd.isna(row['ADDRESS']) else ""

                    # Validate required fields
                    if not payee_name:
                        results.append({
                            'payee_name': payee_name,
                            'mobile_no': mobile_no,
                            'email': email,
                            'address': address,
                            'status': 'Invalid',
                            'error_message': 'Missing required field.',
                        })

                    elif mobile_no in seen_mobiles:
                        results.append({
                            'payee_name': payee_name,
                            'mobile_no': mobile_no,
                            'email': email,
                            'address': address,
                            'status': 'Duplicate',
                            'error_message': 'Duplicate mobile number in file',
                        })

                    elif Payee.objects.filter(mobile_no=mobile_no).exists():
                        results.append({
                            'payee_name': payee_name,
                            'mobile_no': mobile_no,
                            'email': email,
                            'address': address,
                            'status': 'Exists',
                            'error_message': 'Mobile number already exists in database',
                        })

                    else:
                        valid_row = {
                            'payee_name': payee_name,
                            'mobile_no': mobile_no,
                            'email': email,
                            'address': address,
                        }
                        results.append({
                            **valid_row,
                            'status': 'Valid',
                            'error_message': 'Uploading',
                        })
                        valid_rows.append(valid_row)
                        seen_mobiles.add(mobile_no)

                except KeyError as e:
                    results.append({
                        'payee_name': row.get('PAYEE NAME*', None),
                        'mobile_no': row.get('MOBILE NUMBER', None),
                        'email': row.get('EMAIL', None),
                        'address': row.get('ADDRESS', None),
                        'status': 'Invalid',
                        'error_message': f'Missing field: {str(e)}',
                    })

            # Save valid rows in the session for later processing
            request.session['valid_rows'] = valid_rows

            return JsonResponse({'results': results, 'has_valid': len(valid_rows) > 0})
        except Exception as e:
            print(f"Error processing file: {str(e)}")
            return JsonResponse({'error': f"Error processing file: {str(e)}"}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=405)





@csrf_exempt
def save_valid_data_payee(request):
    if request.method == 'POST':
        try:
            
            # session_id = request.session.get('temp_data_key')

            # if not session_id:
            #     return JsonResponse({'success': False, 'error': 'Session ID not found'})

        
            # temp_data = TempDatas.objects.get(session_id=session_id)
            # valid_data = temp_data.data  # Fetch the stored JSON data
            
            
            # Load valid rows from session or a temporary store
            # Assuming they are sent back in a request body or stored in session
            valid_data = request.session.get('valid_rows', [])
            
            for row in valid_data:
                Payee.objects.create(
                    payee_name=row['payee_name'].title(),
                    mobile_no=row['mobile_no'],
                    email=row['email'],
                    address=row['address'],
                    created_by=request.user.id,
                    created_date=datetime.now(),
                    modified_by=request.user.id,
                    modified_date=datetime.now(),
                )
            messages.success(request,"Payee Uploaded Successfully")
            
            if 'valid_rows' in request.session:
                del request.session['valid_rows']
                print("Payee key IN SESSION DELETED")
                request.session.modified = True  # Ensures session updates
            
            # # Delete temporary data after processing
            # temp_data.delete()
            
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})



@login_required
def download_sample_payee(request):
    
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=Sample_Payee_ChequePay.xlsx'
    workbook = openpyxl.Workbook()
    worksheet = workbook.active
    worksheet.title = "Payees"
    
    # columns
    columns = ['PAYEE NAME*', 'MOBILE NUMBER','EMAIL','ADDRESS']
    for col_num, column_title in enumerate(columns, 1):
        cell = worksheet.cell(row=1, column=col_num)
        cell.value = column_title
        cell.font = openpyxl.styles.Font(bold=True)
        cell.fill = PatternFill(start_color="CCCCCC", end_color="CCCCCC", fill_type="solid")  # Gray background

    # data
    banks = [{'payee_name': 'Hussain','mobile_no':'123456','email':'hu@mail.com','address': 'Udaipur'},
             {'payee_name': 'Hassan','mobile_no':'968789','email':'ha@mail.com','address': 'Udaipur'},
             {'payee_name': 'Ali','mobile_no':'123698','email':'a@mail.com','address': 'Udaipur'},
             {'payee_name': 'Abbas','mobile_no':'456312','email':'a@mail.com','address': 'Udaipur'},
             {'payee_name': 'Faraz','mobile_no':'874369','email':'f@mail.com','address': 'Udaipur'},
             
             ]
    
    row = 2
    for bank in banks:
        worksheet.cell(row=row, column=1).value = bank['payee_name']
        worksheet.cell(row=row, column=2).value = bank['mobile_no']
        worksheet.cell(row=row, column=3).value = bank['email']
        worksheet.cell(row=row, column=4).value = bank['address']
        
        row += 1

    # Autofit column widths
    for column in worksheet.columns:
        max_length = 0
        for cell in column:
            max_length = max(max_length, len(str(cell.value)))
        adjusted_width = (max_length + 2) * 1.2
        col_letter = get_column_letter(column[0].column)
        worksheet.column_dimensions[col_letter].width = adjusted_width

    # Correct table reference after all rows are added
    table_ref = f"A1:D{row - 1}"  # Use the correct end row number
    table = Table(displayName='Payees', ref=table_ref)
    worksheet.add_table(table)

    workbook.save(response)
    
    return response