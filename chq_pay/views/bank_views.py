''' The Project 'Cheque Printer' is solely created by Faraz Ahmed Raj - Python Developer
in 2024-2025.'''

from .imp_libs import *
from chq_pay.models import Banks, Company_Setup, ChequeIssue, ChequeTemplate

@login_required
def add_bank(request):
    if request.method == "POST":
        try:
            bank_char = request.POST.get("bank_char")
            bank_name_e = request.POST.get("bank_name_e")
            bank_name_l = request.POST.get("bank_name_l")
            tel_no = request.POST.get("tel_no")
            address = request.POST.get("address")

            bank_exist = Banks.objects.filter(Q(bank_name_e=bank_name_e) | Q(bank_char=bank_char))

            if bank_exist.exists():
                messages.warning(request, 'Bank Already Exists!!')
            else:
                # Save to the database
                Banks.objects.create(
                    bank_char=bank_char.upper(),
                    bank_name_e=bank_name_e.title(),
                    bank_name_l=bank_name_l.title(),
                    tel_no=tel_no,
                    address=address,
                    created_by=request.user.id,
                    created_date=datetime.now(),
                    modified_by=request.user.id,
                    modified_date=datetime.now()
                )
                messages.success(request, 'Bank Created Successfully!!!')
                return JsonResponse({"success": True})
        except Exception as e:
            logger.info(f"Error while adding bank: {e}")
            messages.error(request, "An unexpected error occurred while adding the bank.")
    return JsonResponse({"success": False})

@login_required
def bank_list(request):
    banks = Banks.objects.order_by('bank_char')

    #pagination
    per_page = 10
    paginator = Paginator(banks, per_page)
    page_number = request.GET.get('page')
    banks_list = paginator.get_page(page_number)
    #pagination

    return render(request,"Banks/bank_list_new.html",{'banks':banks_list})

@login_required
def delete_bank(request, bank_id):
    bank_exists = ChequeTemplate.objects.filter(bank=bank_id).exists()
    
    if not bank_exists:
        bank = get_object_or_404(Banks, id=bank_id)
        bank.delete()
        messages.success(request,('Bank Deleted Successfully!!!'))
        return redirect('bank_list')
    else:
        messages.error(request,('Cannot delete this bank, a template exists with this bank.!!'))
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
        
        
        # Update the bank in the database
        try:
            bank = Banks.objects.get(id=bank_id)
            bank.bank_char = bank_char.upper()
            bank.bank_name_e = bank_name_e.title()
            bank.bank_name_l = bank_name_l.title()
            bank.tel_no = tel_no
            bank.address = address
            bank.modified_by = request.user.id
            bank.modified_date = datetime.now()

            bank_exist = Banks.objects.filter(Q(bank_name_e=bank_name_e) | Q(bank_char=bank_char)).exclude(id=bank_id)

            if bank_exist:
                messages.warning(request,('Bank with same name or bank char already exits!!'))

            else:
                
                bank.save()
                messages.success(request,('Bank Details Updated Successfully!!!'))
                return JsonResponse({"success": True})
        except Banks.DoesNotExist:
            messages.error(request,('Error in Bank Updation!!'))
            return JsonResponse({"success": False, "error": "Bank not found"})
    return JsonResponse({"success": False, "error": "Invalid request"})



@csrf_exempt
@login_required
def validate_excel_bank(request):
    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES['file']
        try:
            # Load the Excel file
            df = pd.read_excel(file)

            # Ensure the headers match the expected column names
            expected_columns = ['BANK CHAR*', 'BANK NAME ENGLISH*', 'BANK NAME LOCAL*', 'TELEPHONE NO.', 'ADDRESS']
            if list(df.columns) != expected_columns:
                return JsonResponse({
                    'error': 'Invalid file format. Ensure the headers are: {}'.format(", ".join(expected_columns))
                }, status=400)

            results = []
            valid_rows = []

            # Iterate through rows to validate data
            for _, row in df.iterrows():
                try:
                    bank_char = row['BANK CHAR*']
                    bank_name_e = row['BANK NAME ENGLISH*']
                    bank_name_l = row['BANK NAME LOCAL*']
                    tel_no = row['TELEPHONE NO.']
                    address = row['ADDRESS']

                    # Check for missing fields
                    if pd.isna(bank_char) or pd.isna(bank_name_e) or pd.isna(bank_name_l):

                        bank_char = "" if pd.isna(bank_char) else bank_char
                        bank_name_e = "" if pd.isna(bank_name_e) else bank_name_e
                        bank_name_l = "" if pd.isna(bank_name_l) else bank_name_l
                        tel_no = "" if pd.isna(tel_no) else tel_no
                        address = "" if pd.isna(address) else address
                        
                        
                        results.append({
                            'bank_char': bank_char,
                            'bank_name_e': bank_name_e,
                            'bank_name_l': bank_name_l,
                            'tel_no': tel_no,
                            'address': address,
                            'status': 'Invalid',
                            'error_message': 'Missing required fields',
                        })
                    
                    elif Banks.objects.filter(Q(bank_char=bank_char) | Q(bank_name_e=bank_name_e)).exists():

                        results.append({
                            'bank_char': bank_char,
                            'bank_name_e': bank_name_e,
                            'bank_name_l': bank_name_l,
                            'tel_no': tel_no,
                            'address': address,
                            'status': 'Exists',
                            'error_message': 'Bank already exists',
                        })

                    else:
                        valid_row = {
                            'bank_char': bank_char,
                            'bank_name_e': bank_name_e,
                            'bank_name_l': bank_name_l,
                            'tel_no': tel_no,
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
                        'bank_char': row.get('BANK CHAR*', None),
                        'bank_name_e': row.get('BANK NAME ENGLISH*', None),
                        'bank_name_l': row.get('BANK NAME LOCAL*', None),
                        'tel_no': row.get('TELEPHONE NO.', None),
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
def save_valid_data_bank(request):
    if request.method == 'POST':
        try:
            # Load valid rows from session or a temporary store
            # Assuming they are sent back in a request body or stored in session
            valid_data = request.session.get('valid_rows', [])
            
            for row in valid_data:
                Banks.objects.create(
                    bank_char=row['bank_char'],
                    bank_name_e=row['bank_name_e'],
                    bank_name_l=row['bank_name_l'],
                    tel_no=row['tel_no'],
                    address=row['address'],
                    created_by=request.user.id,
                    created_date=datetime.now(),
                    modified_by=request.user.id,
                    modified_date=datetime.now(),
                )
            messages.success(request,"Banks Uploaded Successfully")
            return JsonResponse({'success': True})
        except Exception as e:
            messages.error(request,"Bank Upload Failed!!")
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})



@login_required
def download_sample_bank(request):
    
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=Sample_Bank_ChequePay.xlsx'
    workbook = openpyxl.Workbook()
    worksheet = workbook.active
    worksheet.title = "Banks"
    
    # columns
    columns = ['BANK CHAR*', 'BANK NAME ENGLISH*','BANK NAME LOCAL*', 'TELEPHONE NO.','ADDRESS']
    for col_num, column_title in enumerate(columns, 1):
        cell = worksheet.cell(row=1, column=col_num)
        cell.value = column_title
        cell.font = openpyxl.styles.Font(bold=True)
        cell.fill = PatternFill(start_color="CCCCCC", end_color="CCCCCC", fill_type="solid")  # Gray background

    # data
    banks = [{'bank_char': 'SBI','bank_name_e':'State Bank Of India','bank_name_l':'State Bank Of India','tel_no': '123456','address': 'Udaipur'},
             {'bank_char': 'AXIS','bank_name_e':'Axis Bank Ltd.','bank_name_l':'Axis Bank Ltd.','tel_no': '123456','address': 'Udaipur'},
             {'bank_char': 'FEDERAL','bank_name_e':'Federal Bank Ltd.','bank_name_l':'Federal Bank Ltd.','tel_no': '123456','address': 'Udaipur'},
             {'bank_char': 'HDFC','bank_name_e':'HDFC Bank Ltd.','bank_name_l':'HDFC Bank Ltd.','tel_no': '123456','address': 'Udaipur'},
             {'bank_char': 'ICICI','bank_name_e':'ICICI Bank Ltd.','bank_name_l':'ICICI Bank Ltd.','tel_no': '123456','address': 'Udaipur'},
             ]
    
    row = 2
    for bank in banks:
        worksheet.cell(row=row, column=1).value = bank['bank_char']
        worksheet.cell(row=row, column=2).value = bank['bank_name_e']
        worksheet.cell(row=row, column=3).value = bank['bank_name_l']
        worksheet.cell(row=row, column=4).value = bank['tel_no']
        worksheet.cell(row=row, column=5).value = bank['address']
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
    table_ref = f"A1:E{row - 1}"  # Use the correct end row number
    table = Table(displayName='Banks', ref=table_ref)
    worksheet.add_table(table)

    workbook.save(response)
    
    return response
