''' The Project 'Cheque Printer' is solely created by Faraz Ahmed Raj - Python Developer
in 2024-2025.'''

from .imp_libs import *
from django.db.migrations.executor import MigrationExecutor
from chq_pay.models import AppUser, Company_Setup
from datetime import datetime



# Get the custom user model
User = get_user_model()

@login_required
@custom_permission_required
def users_list(request):
    present_users = User.objects.all().order_by('username')

    #pagination
    per_page = 25
    paginator = Paginator(present_users, per_page)
    page_number = request.GET.get('page')
    user_list = paginator.get_page(page_number)
    #pagination

    return render(request,"Users/user_list.html",{'users_present':user_list})


@login_required
@custom_permission_required
def add_user(request):
    if request.method == "POST":
        first_name = request.POST.get("user_first_name")
        last_name = request.POST.get("user_last_name")
        email = request.POST.get("user_email")
        privilege_role = request.POST.get("user_role")
        password = request.POST.get("user_password")
        profile_picture = request.FILES.get("user_pp")
        is_admin = request.POST.get("is_admin")

        print("admin - ", type(is_admin))
        
        user_exist = User.objects.filter(Q(username=email))

        if user_exist:
            messages.error(request,('User Already Exits!!'))
        else:
            # Save to the database
            user_adding = User(
                username=email,
                email = email,
                first_name=first_name,
                last_name = last_name,
                privilege_role = privilege_role,
                )
            if profile_picture:
                user_adding.profile_picture = profile_picture
            
            if is_admin == 'true':
                user_adding.is_superuser = True
                user_adding.is_staff = True
            
            # Hash the password before saving
            user_adding.set_password(password)
            
            user_adding.save()
            messages.success(request,('User Created Successfully!!!'))
            return JsonResponse({"success": True})
    return JsonResponse({"success": False})


@login_required
@custom_permission_required
def edit_user(request):
    if request.method == "POST":
        user_id = request.POST.get("user_id")
        first_name = request.POST.get("user_first_name")
        last_name = request.POST.get("user_last_name")
        email = request.POST.get("user_email")
        privilege_role = request.POST.get("user_role")
        profile_picture = request.FILES.get("user_pp")
        is_admin = request.POST.get("is_admin")


        usr_exist = User.objects.filter(username=email).exclude(id=user_id).exists()

        if usr_exist:
            messages.error(request,('User Already Exits!!'))
        else:
            # Save to the database
            try:
                edit_usr = get_object_or_404(User, id = user_id)

                edit_usr.first_name = first_name
                edit_usr.last_name = last_name
                edit_usr.username = email
                edit_usr.email = email
                edit_usr.privilege_role = privilege_role

                if is_admin == "true":
                    edit_usr.is_superuser = True
                    edit_usr.is_staff = True
                elif User.objects.filter(is_superuser=True).count() <= 1:
                    messages.warning(request,('There Needs To Be Atleast One Admin.'))
                else:
                    edit_usr.is_superuser = False
                    edit_usr.is_staff = False


                if profile_picture:
                    edit_usr.profile_picture = profile_picture

                edit_usr.save()

                print("logged user id -  ", request.user.id)
                print("given user id -  ",user_id )
                
                if request.user.id == int(user_id):
                    request.session.flush()
                    logout(request)
                
                messages.success(request,('User Details Updated Successfully!!!'))
                return JsonResponse({"success": True})
                
            except Company_Setup.DoesNotExist:
                return JsonResponse({"success": False, "error": "User not found"})
    return JsonResponse({"success": False, "error": "Invalid request"})



@login_required
@custom_permission_required
def delete_user(request, user_id):
    usr = get_object_or_404(User, id=user_id)

    if usr.is_superuser:
        messages.error(request,('Admin Cannot Be Deleted'))
    else:
        usr.delete()
        messages.success(request,('User Deleted Successfully!!!'))
    return redirect('users_list')