''' The Project 'Cheque Printer' is solely created by Faraz Ahmed Raj - Python Developer
in 2024-2025.'''

from .imp_libs import *
from django.db.migrations.executor import MigrationExecutor


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

def create_user_if_needed(password,email,name):
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
        sess_expiry_date = license_data.get('expiry_date', None)
        expiry_dt_time = datetime.strptime( sess_expiry_date, "%Y-%m-%d %H:%M:%S") #setting to right fromat to compare expiry date

        if not all([sess_reg_code, sess_email, sess_password, sess_name, sess_expiry_date]):
            print("incomplete session data")

       
        try:
            if reg_code == sess_reg_code:
                print("code matched")
                if expiry_dt_time >= datetime.now():
                    
                    user = create_user_if_needed(sess_password, sess_email, sess_name )

                    user = authenticate(request, username=username, password=password)
                
                    if user:
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