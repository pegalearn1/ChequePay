''' The Project 'Cheque Printer' is solely created by Faraz Ahmed Raj - Python Developer
in 2024-2025.'''

from .imp_libs import *
from django.db.migrations.executor import MigrationExecutor
from chq_pay.models import AppUser, Company_Setup
from datetime import datetime

# Get the custom user model
User = get_user_model()


def check_table_exists(reg_code):
    """
    Checks if a specific table exists in the specified database.
    Returns True if table exists, otherwise False.
    """
    connection = connections[reg_code]
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='chq_pay_chqpayuser';")
            return bool(cursor.fetchone())
    except OperationalError:
        return False
    

def apply_migrations_to_db(connection):
    """
    Apply all migrations to the specified database connection.
    """
    try:
        executor = MigrationExecutor(connection)
        executor.migrate(executor.loader.graph.leaf_nodes())
        print(f"Migrations applied to database: {connection.alias}")
    except Exception as e:
        print(f"Migration error: {e}")


def create_user_if_needed(reg_code, email, password, name, license_key, cust_id, country_id, country_name, allowed_templates,expiry_date, company, phone, address):
    """
    If the table doesn't exist in the specified database, apply migrations to create it.
    Then create a new user if the table was successfully created.
    """
    connection = connections[reg_code]
    print(f"Using database: {connection.alias}")

    # Check if the table exists in the specified database
    if not check_table_exists(reg_code):
        print("Table does not exist. Applying migrations...")
        try:
            apply_migrations_to_db(connection)
        except Exception as e:
            print("migration error - ", str(e) )
        
        # After migrations, recheck the table existence
        if check_table_exists(reg_code):
            print("Table created successfully.")


            AppUser.objects.using(connection.alias).create(
                reg_code=reg_code,
                license_key=license_key,
                name=name,
                email=email,
                cust_id=cust_id,
                country_id=country_id,
                country_name=country_name,
                allowed_templates=allowed_templates,
                expiry_date = expiry_date
            )
            print("App User Updated")
            
            Company_Setup.objects.using(connection.alias).create(
                registration_id=reg_code,
                company_name=company,
                is_selected=True,
                tel_no=phone,
                email=email,
                address=address,
                created_by=1,
                created_date=datetime.now(),
                modified_by=1,
                modified_date=datetime.now()
            )

            print("Company Created")

            user = User.objects.using(connection.alias).create(
                username=email,
                password=make_password(password),
                email=email,
                first_name=name,
                privilege_role='SuperAdmin',
                is_superuser=True,
                is_staff=True
            )
            print("User Created")

           
            return user
        
        else:
            print("Table creation failed after migrations.")

    return None



@csrf_exempt
def user_login(request):

    registration_code_url = request.GET.get('reg_code')


    if request.method == "POST":
        # Getting values from template
        reg_code = request.POST.get('login_reg_code')
        username = request.POST.get('login_email')
        password = request.POST.get('login_password')

        if not reg_code or len(reg_code) < 4:
            logger.info("Invalid registration code: %s", reg_code)
            

        # Fetch data from the APIs
        logger.info("Preparing API calls...")
        
        payload = {"lic_code": reg_code, "master_product_id": "865"}
        logger.info("Payload prepared: %s", payload)

        logger.info("Making API call to URL1...")
        response1 = requests.post(url1, data=payload)
        logger.info("Response from URL1: Status %d", response1.status_code)

        logger.info("Making API call to URL2...")
        response2 = requests.post(url2, data=payload)
        logger.info("Response from URL2: Status %d", response2.status_code)

        # Parse responses
        logger.info("Parsing responses...")
        response1.raise_for_status()
        res1 = response1.json()
        logger.info("Response from URL1 parsed: %s", res1)

        response2.raise_for_status()
        res2 = response2.json()
        logger.info("Response from URL2 parsed: %s", res2)

        if res1['status'] is True:
            logger.info("API status is True for res1. Extracting data...")

            expdt = res1['result']['expiry_date']
            license_key = res1['result']['license_key']
            registcode = res1['result']['registration_code']
            eml = res1['result']['email']
            cust_id = res1['result']['customer_id']
            nme = res1['result']['name']
            cmpny = res1['result']['company_name']
            phn = res1['result']['phone']
            licnse_type = res1['result']['product_type']
            cntry_id = res1['result']['country_id']
            dtbs = res1['result']['database']
            addrs = res1['result']['address']
            cty = res1['result']['city']
            currency = res1['result']['currency_symbol']
            country_name = res1['result']['country']
            passw = res1['result']['password']

        if res2['status'] is True:
            logger.info("API status is True for res2. Extracting data...")

            templates_api = res2['result'][0]['param_value']


        try:
            logger.info("Saving registration code to session.")
            request.session['reg_code'] = registcode
            request.session.modified = True
            logger.info("Registration code saved to session successfully.")
        except Exception as e:
            logger.error("Error saving registration code to session: %s", e)

        try:
            expiry_dt_time = datetime.strptime(expdt, "%Y-%m-%d %H:%M:%S")
        except Exception as e:
            logger.info("Error parsing expiry date: %s", str(e))
            return redirect('login')

        try:
            if reg_code == registcode:
                logger.info("Registration code matched.")

                if expiry_dt_time >= datetime.now():
                    logger.info("License is valid.")

                    user = create_user_if_needed(
                        registcode, eml, passw, nme,
                        license_key, cust_id, cntry_id, country_name,
                        templates_api,expdt, cmpny, phn, addrs
                    )

                    from django.db import connections

                    db_alias = registcode

                    # Ensure the connection exists
                    if db_alias in connections.databases:
                        connections[db_alias].ensure_connection()
                        logger.info(f"Database alias {db_alias} connection made")
                        print(f"Database alias {db_alias} connection made")
                    else:
                        logger.info(f"Database alias {db_alias} is not found in Django settings.")
                        return redirect('login')

                    
                    user = User.objects.using(registcode).get(username=username)

                    if user:
                        if user.check_password(password):
                            logger.info("User exists and password is correct.")

                            login(request, user)
                            

                            logger.info(f"Logged In with {user}.")

                            return redirect('setup_wizard')
                        else:
                            logger.info("Invalid login credentials: Incorrect password!!")
                            messages.error(request, 'Invalid login credentials: Incorrect password!!')
                    else:
                        logger.info("Invalid login credentials: User does not exist!!")
                        messages.error(request, 'Invalid login credentials: User does not exist!!')

                    
                else:
                    logger.info("License expired.")
                    messages.error(request, 'License expired, please renew or upgrade the license.')
            else:
                logger.info("Invalid registration code.")
                messages.error(request, 'Invalid Registration Code!!')
        except Exception as e:
            logger.info("Exception during login: %s", str(e))
            return redirect('login')

    return render(request, "Login/login.html",{'registration_code_url':registration_code_url})


@login_required
def user_logout(request):
    try:
        request.session.flush()
        logout(request)
        return redirect('home')
    except:
        messages.error(request, "Error in Logging Out !!")

    return render(request, 'Login/login.html')

