''' The Project 'Cheque Printer' is solely created by Faraz Ahmed Raj - Python Developer
in 2024-2025.'''

from .imp_libs import *
from django.contrib.auth import get_user_model

# Get the custom user model
User = get_user_model()

def user_login(request):

    if request.method == "POST":
        #getting values from template
        username = request.POST.get('login_email')
        password = request.POST.get('login_password')
        # reg_code = request.POST.get('reg_code')

        print("username - ",username)
        print("password - ",password)

        try:
            # request.session.flush()
            user = authenticate(request, username=username, password=password)
            
            if user:
                login(request, user)
                return redirect('index')
            else:
                messages.error(request, 'Invalid login credentials!!')
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
        return redirect('login')
    except:
        messages.error(request, "Error in Logging Out !!")

    return render(request, 'Login/login.html')

def user_profile(request):
    return render(request, "home/profile.html")