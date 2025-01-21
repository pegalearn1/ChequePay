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
        address = request.POST.get("payee_address")
        
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

            if address:
                payee.address = address
                payee.save()
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
        address = request.POST.get("payee_address")
        print("payeee = ",payee_id)
        
        # Update the bank in the database
        try:
            payee = Payee.objects.get(id=payee_id)
            payee.payee_name = payee_name
            payee.mobile_no = mobile_no
            payee.email = email
            payee.modified_by = request.user.id
            payee.modified_date = datetime.now()

            if address:
                payee.address = address
            
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




@csrf_exempt
@login_required
def validate_excel_payee(request):
    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES['file']
        try:
            # Load the Excel file
            df = pd.read_excel(file)

            # Ensure the headers match the expected column names
            expected_columns = ['PAYEE NAME', 'MOBILE NUMBER', 'EMAIL', 'ADDRESS']
            if list(df.columns) != expected_columns:
                return JsonResponse({
                    'error': 'Invalid file format. Ensure the headers are: {}'.format(", ".join(expected_columns))
                }, status=400)

            results = []
            valid_rows = []

            # Iterate through rows to validate data
            for _, row in df.iterrows():
                try:
                    payee_name = row['PAYEE NAME']
                    mobile_no = row['MOBILE NUMBER']
                    email = row['EMAIL']
                    address = row['ADDRESS']

                    # Check for missing fields
                    if pd.isna(payee_name) or pd.isna(mobile_no) or pd.isna(email) or pd.isna(address):

                        payee_name = "" if pd.isna(payee_name) else payee_name
                        mobile_no = "" if pd.isna(mobile_no) else mobile_no
                        email = "" if pd.isna(email) else email
                        address = "" if pd.isna(address) else address
                        
                        
                        results.append({
                            'payee_name': payee_name,
                            'mobile_no': mobile_no,
                            'email': email,
                            'address': address,
                            'status': 'Invalid',
                            'error_message': 'Missing required fields',
                        })
                    
                    elif Payee.objects.filter(payee_name = payee_name).exists():

                        results.append({
                            'payee_name': payee_name,
                            'mobile_no': mobile_no,
                            'email': email,
                            'address': address,
                            'status': 'Exists',
                            'error_message': 'Payee already exists',
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
                
            
                except KeyError as e:
                    
                    # If a specific field is missing in the row, capture the error
                    results.append({
                        'payee_name': row.get('PAYEE NAME', None),
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
            # Log the exception and return a detailed error message
            print(f"Error processing file: {str(e)}")
            return JsonResponse({'error': f"Error processing file: {str(e)}"}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=405)



@csrf_exempt
def save_valid_data_payee(request):
    if request.method == 'POST':
        try:
            # Load valid rows from session or a temporary store
            # Assuming they are sent back in a request body or stored in session
            valid_data = request.session.get('valid_rows', [])
            
            for row in valid_data:
                Payee.objects.create(
                    payee_name=row['payee_name'],
                    mobile_no=row['mobile_no'],
                    email=row['email'],
                    address=row['address'],
                    created_by=request.user.id,
                    created_date=datetime.now(),
                    modified_by=request.user.id,
                    modified_date=datetime.now(),
                )
            messages.success(request,"Payee Uploaded Successfully")
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
    columns = ['PAYEE NAME', 'MOBILE NUMBER','EMAIL','ADDRESS']
    for col_num, column_title in enumerate(columns, 1):
        cell = worksheet.cell(row=1, column=col_num)
        cell.value = column_title
        cell.font = openpyxl.styles.Font(bold=True)
        cell.fill = PatternFill(start_color="CCCCCC", end_color="CCCCCC", fill_type="solid")  # Gray background

    # data
    banks = [{'payee_name': 'Hussain','mobile_no':'123456','email':'hu@mail.com','address': 'Udaipur'},
             {'payee_name': 'Hassan','mobile_no':'123456','email':'ha@mail.com','address': 'Udaipur'},
             {'payee_name': 'Ali','mobile_no':'123456','email':'a@mail.com','address': 'Udaipur'},
             {'payee_name': 'Abbas','mobile_no':'123456','email':'a@mail.com','address': 'Udaipur'},
             {'payee_name': 'Faraz','mobile_no':'123456','email':'f@mail.com','address': 'Udaipur'},
             
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