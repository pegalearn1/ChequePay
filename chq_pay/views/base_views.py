''' The Project 'Cheque Printer' is solely created by Faraz Ahmed Raj - Python Developeris_selected
in 2024-2025.'''

from .imp_libs import *
from chq_pay.models import Banks, Payee, ChequeTemplate, ChequeIssue, Currencies,Company_Setup
from django.contrib.auth.hashers import check_password


# from rembg import remove
from django.core.files.base import ContentFile
from PIL import Image
import io
from django.core.files.base import ContentFile

# Get the custom user model
User = get_user_model()

def home(request):
    return render(request, "home/home.html")

@login_required
def base_temp(request):
    return render(request, "layouts/base.html")

@login_required
def index(request):

    current_host = 'http://' + request.get_host()
    csrf_origins = settings.CSRF_TRUSTED_ORIGINS
    if current_host not in csrf_origins:
        # Add the current host to the CSRF_TRUSTED_ORIGINS
        csrf_origins.append(current_host)
        settings.CSRF_TRUSTED_ORIGINS = csrf_origins
        print("Updated CSRF_TRUSTED_ORIGINS:", settings.CSRF_TRUSTED_ORIGINS)
        

#for certain counts
    bank_count = Banks.objects.count()
    payee_count = Payee.objects.count()
    template_count = ChequeTemplate.objects.filter(company__is_selected = True).count()
    currency_count = Currencies.objects.count()
    
#for cheque counts
    total_cheques = ChequeIssue.objects.filter(company__is_selected = True).count()
    approved_cheques = ChequeIssue.objects.filter(company__is_selected = True, issue_is_approved = True).count()
    pending_cheques = ChequeIssue.objects.filter(company__is_selected = True, issue_is_approved = None).count()
    rejected_cheques = ChequeIssue.objects.filter(company__is_selected = True, issue_is_approved = False).count()

#for cheque issue  pie chart
    #chart cheque issue bank template labels
    cheque_issue = ChequeIssue.objects.values_list("issue_bank", flat=True)
    banks_cheque = Banks.objects.filter(id__in=cheque_issue).distinct().order_by('bank_name_e')

    bank_names_issue = list(banks_cheque.values_list('bank_name_e', flat=True))
   
    #chart cheque issue values
    chq_iss = []
    for bnk in banks_cheque:
        iss_chq = ChequeIssue.objects.filter(company__is_selected = True, issue_bank = bnk).filter(issue_is_approved = True).count()
        chq_iss.append(str(iss_chq))

    cheque_issued = ','.join(chq_iss)

    #pie chart colors for cheque issue
    cheque_issue_color = []
    for chq_color in range(template_count):
        random_color = (randrange(255), randrange(255), randrange(255))
        cheque_issue_color.append(f'rgb({random_color[0]}, {random_color[1]}, {random_color[2]})')



#for bank template pie chart
    #chart cheque issue bank template labels
    cheque_tem = ChequeTemplate.objects.values_list("bank", flat=True)
    banks_tem = Banks.objects.filter(id__in=cheque_tem).distinct().order_by('bank_name_e')

    bank_names_temp = list(banks_tem.values_list('bank_name_e', flat=True))

    #chart bank template values
    chq_temps = []
    for bnk in banks_tem:
        bank_temps = ChequeTemplate.objects.filter(company__is_selected = True, bank = bnk).count()
        chq_temps.append(str(bank_temps))

    bank_templates = ','.join(chq_temps)

    #pie chart colors for bank template
    template_color = []
    for temp_color in range(template_count):
        random_color = (randrange(255), randrange(255), randrange(255))
        template_color.append(f'rgb({random_color[0]}, {random_color[1]}, {random_color[2]})')



#for currency-transact-pie  pie chart
    #chart currency-transact labels
    currencies = Currencies.objects.order_by('currency_name')
    currency_char = list(currencies.values_list('currency_name', flat=True))

    
    #chart currency-transact values
    cur_transct = []
    for cur in currencies:
        currency_transact = ChequeIssue.objects.filter(company__is_selected = True, issue_currency = cur, issue_is_approved = True).values_list('issue_amount', flat=True)
        if currency_transact: cur_transct.append(str(sum(currency_transact)))
    
    currency_transactions = ','.join(cur_transct)

    

    #pie chart colors for currency-transact
    currency_trans_color = []
    for cur_color in range(currency_count):
        random_color = (randrange(255), randrange(255), randrange(255))
        currency_trans_color.append(f'rgb({random_color[0]}, {random_color[1]}, {random_color[2]})')


    




    
    
    context = {
        'bank_count':bank_count,
        'payee_count':payee_count,
        'template_count':template_count,
        'currency_count':currency_count,
        'chq_issue_count':approved_cheques,
        'bank_names_issue':bank_names_issue,
        'bank_names_temp':bank_names_temp,
        'cheque_issued':cheque_issued,
        'cheque_issue_colors':cheque_issue_color,
        'bank_templates':bank_templates,
        'template_color':template_color,
        'total_cheques':total_cheques,
        'approved_cheques':approved_cheques,
        'pending_cheques':pending_cheques,
        'rejected_cheques':rejected_cheques,
        'currency_char':currency_char,
        'currency_trans_color':currency_trans_color,
        'currency_transactions':currency_transactions,

        }

    return render(request, "home/index.html", context)


# def remove_background(image_file):
#     """
#     Removes background from the uploaded image file and returns a processed image.
#     """
#     try:
#         # Open the image
#         img = Image.open(image_file)
        
#         # Convert to RGBA (if not already)
#         img = img.convert("RGBA")

#         # Remove background
#         img_no_bg = remove(img)

#         # Save to memory
#         img_io = io.BytesIO()
#         img_no_bg.save(img_io, format="PNG")
        
#         return ContentFile(img_io.getvalue(), name=image_file.name)  # Preserve original filename

#     except Exception as e:
#         print(f"Error processing signature: {e}")
#         return None


def remove_background(image_file):
    """
    Removes white background from uploaded signature image and returns transparent PNG.
    """
    try:
        # Open the image
        img = Image.open(image_file).convert("RGBA")
        datas = img.getdata()

        newData = []
        for item in datas:
            # item is (R, G, B, A)
            if item[0] > 200 and item[1] > 200 and item[2] > 200:
                # If pixel is "almost white" (tune threshold if needed)
                newData.append((255, 255, 255, 0))  # Make pixel fully transparent
            else:
                newData.append(item)

        img.putdata(newData)

        # Save to memory
        img_io = io.BytesIO()
        img.save(img_io, format="PNG")

        return ContentFile(img_io.getvalue(), name=image_file.name)

    except Exception as e:
        print(f"Error processing signature: {e}")
        return None

@login_required
def profile(request):
    from django.db import connection
    print("Database in use start:", connection.settings_dict['NAME'])

    if request.method == 'POST':
        try:
            username = request.POST.get('username')
            email = request.POST.get('email')
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            password = request.POST.get('password')
            profile_picture = request.FILES.get('profile_picture')
            sign = request.FILES.get('sign')

            print("POST values:")
            print("Username: ", username)
            print("Email: ", email)
            print("First Name: ", first_name)
            print("Last Name: ", last_name)
            print("Password: ", password)

            print("Session data:", request.session.items())  # Debug session data
            print("Using Database:", connection.settings_dict['NAME'])  # Show the database in use

            usr = get_object_or_404(User, username=username)

            usr.email = email
            usr.first_name = first_name
            usr.last_name = last_name

            if profile_picture:
                usr.profile_picture = profile_picture

            if sign:
                processed_sign = remove_background(sign)  # Remove background
                if processed_sign:
                    usr.auth_sign = processed_sign

            password_changed = False

            if password:
                if not password.startswith(('pbkdf2_sha256$', 'bcrypt', 'sha1$', 'argon2$')):  
                    usr.set_password(password)  # Hash and set new password
                    password_changed = True  # Mark password change

            db_name = request.session.get('reg_code', 'default')
            usr.save(using=db_name)

            messages.success(request, "Profile Updated Successfully")

            if password_changed:
                logout(request)
                messages.info(request, "Password changed successfully. Please log in again.")
                return redirect('login')

            return redirect('profile')

        except Exception as e:
            logger.info(f"Error while updating profile: {str(e)}")
            print("Exception occurred:", str(e))
            messages.error(request, "An error occurred while updating your profile.")
            return redirect('profile')

    return render(request, "home/profile.html")