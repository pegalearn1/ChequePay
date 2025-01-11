''' The Project 'Cheque Printer' is solely created by Faraz Ahmed Raj - Python Developer
in 2024-2025.'''

from .imp_libs import *
from django.db.migrations.executor import MigrationExecutor
from chq_pay.models import AppUser, Company_Setup
from datetime import datetime

# Get the custom user model
User = get_user_model()


def check_table_exists():
    """
    Checks if a specific table exists in the database.
    Returns True if table exists, otherwise False.
    """
    connection = connections['default']
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='chq_pay_chqpayuser';")
            return bool(cursor.fetchone())
    except OperationalError:
        return False

def create_user_if_needed(reg_code, email, password, name, license_key, cust_id, country_id, country_name, allowed_templates, company, phone, address):
    """
    If the table doesn't exist, apply migrations to create it.
    Then create a new user if the table was successfully created.
    """
    # Check if the table exists
    if not check_table_exists():
        # Run migrations to create the table
        executor = MigrationExecutor(connections['default'])
        executor.migrate(executor.loader.graph.leaf_nodes())

        # After migration, create the user
        # Replace this with your user creation logic, for example:
        AppUser.objects.create(reg_code = reg_code, license_key = license_key, name=name, email=email, cust_id=cust_id, country_id=country_id, country_name=country_name, allowed_templates=allowed_templates)
        Company_Setup.objects.create(registration_id = reg_code, company_name = company, is_selected = True, tel_no = phone, email = email, address = address, created_by = 1,created_date = datetime.now(), modified_by = 1, modified_date = datetime.now())
        
        user = User.objects.create_user(
            username=email, 
            password=password, 
            email=email,
            first_name = name,
            is_superuser=True,
            is_staff=True
        )
        
        return user
    
        
    return None




def user_login(request):

    if request.method == "POST":
        #getting values from template
        reg_code = request.POST.get('login_reg_code')
        username = request.POST.get('login_email')
        password = request.POST.get('login_password')

        license_data = request.session.get('license_data', {})
        sess_reg_code = license_data.get('registration_code', None)
        sess_email = license_data.get('email', None)
        sess_password = license_data.get('password', None)
        sess_name = license_data.get('name', None)
        sess_license_key = license_data.get('license_key', None)
        sess_cust_id = license_data.get('customer_id', None)
        sess_country_id = license_data.get('country_id', None)
        sess_country_name = license_data.get('country_name', None)
        sess_allowed_templates = license_data.get('allowed_templates', None)
        sess_expiry_date = license_data.get('expiry_date', None)
        sess_company = license_data.get('company', None)
        sess_phone = license_data.get('phone', None)
        sess_address = license_data.get('address', None)
        expiry_dt_time = datetime.strptime( sess_expiry_date, "%Y-%m-%d %H:%M:%S") #setting to right fromat to compare expiry date

        if not all([sess_reg_code, sess_email, sess_password, sess_name, sess_expiry_date]):
            print("incomplete session data")
        
        
       
        try:
            if reg_code == sess_reg_code:
                print("code matched")
                if expiry_dt_time >= datetime.now():
                    
                    user = create_user_if_needed(sess_reg_code, sess_email, sess_password, sess_name, sess_license_key, sess_cust_id, sess_country_id, sess_country_name, sess_allowed_templates, sess_company, sess_phone, sess_address)

                    user = authenticate(request, username=username, password=password)
                
                    if user:
                        if 'license_data' in request.session:
                            del request.session['license_data']
                            print("license_data removed from session")
                        else:
                            print("license_data not found in session")
                        
                        login(request, user)
                        return redirect('index')
                    else:
                        messages.error(request, 'Invalid login credentials!!')
                else:
                    messages.error(request, 'License expired, please renew or upgrade the license.')
            
            else:
                messages.error(request, 'Invalid Registration Code!!')
        except Exception as e:
            print('login exception', str(e))
            return redirect('login')
    

    return render(request, "Login/login.html")

def user_register(request):
    if request.method == "POST":
        first_name = request.POST.get('register_name')
        email = request.POST.get('register_email')
        password = request.POST.get('register_password')

        # Check if the email already exists
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email is already registered!")
            return redirect('register')

        # Create a new user
        try:
            user = User.objects.create_user(
                username=email,  # Use email as the username
                email=email,
                password=password,
                first_name=first_name
            )
            user.save()

            messages.success(request, "Registration successful! You can now log in.")
            return redirect('login')  # Redirect to login page after successful registration
        except Exception as e:
            messages.error(request, f"Error creating user: {str(e)}")
            return redirect('register')

        
    return render(request, "Login/register.html")


@login_required
def user_logout(request):
    try:
        request.session.flush()
        logout(request)
        return redirect('home')
    except:
        messages.error(request, "Error in Logging Out !!")

    return render(request, 'Login/login.html')

def user_profile(request):
    return render(request, "home/profile.html")