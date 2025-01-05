from django.shortcuts import render, redirect, get_object_or_404, HttpResponseRedirect #to render templates
from django.contrib.auth.decorators import login_required #decorator to make login neccesary for every page
from django.views.decorators.csrf import csrf_exempt #to exempt function from  csrf token
from django.contrib.auth import authenticate, login, logout #native authentication libraries
from datetime import datetime, date
import os
import subprocess
import pdfkit  # Add this import
from django.http import HttpResponse
from django.template.loader import get_template
from django.conf import settings
from django.http import HttpResponseBadRequest
from django.contrib import messages #to send error or success messages
from django.http import JsonResponse #For Json response
from django.db.models import Q #for or options in queries
from num2words import num2words # to convert number into words
from pathlib import Path
from rest_framework.decorators import api_view
import requests
from django.db import connections
from django.core.management import call_command
from django.contrib.auth import get_user_model
from django.db.utils import OperationalError
import json
from django.core.paginator import Paginator



BASE_DIR = Path(__file__).resolve().parent.parent.parent

print(BASE_DIR)

#Created By Faraz Ahmed Raj on 26 December 2023.
# The function is to restrict the access to certain urls in the project which can only be accessed by admin.
from django.http import HttpResponseForbidden
def custom_permission_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_staff:
            return HttpResponseForbidden("You don't have permission to access this page.")
        return view_func(request, *args, **kwargs)
    return wrapper
# The function is to restrict the access to certain urls in the project which can only be accessed by admin.



# global variable for site for apis

api_call_site = "https://www.pegasustech.net"

api_call_site2 = "http://74.208.235.72/pegasus"

# global variable for site for apis

@csrf_exempt
def check_reg_update_sett(request):

    print("Request received!")  # Check if the function is called
    print("Request method:", request.method)  # Check the request method

    try:
        print("Parsing request body...")
        data = json.loads(request.body)
        print("Request data parsed:", data)

        reg_code = data.get('reg_code')
        print("Registration code:", reg_code)

        if not reg_code or len(reg_code) < 4:
            print("Invalid registration code")
            return JsonResponse({"status": "error", "message": "Invalid registration code"}, status=400)

        # Fetch data from the APIs
        print("Making API calls...")
        url1 = f"{api_call_site}/index.php?route=api/license_product_3/get_detail"
        url2 = f"{api_call_site}/index.php?route=api/license_product_3/lic_parameter"
        
        payload = {"lic_code": reg_code, "master_product_id": "865"}
        print("Payload:", payload)

        response1 = requests.post(url1, data=payload) #getting data from 1st url
        print("Response from URL1 received. Status:", response1.status_code)

        response2 = requests.post(url2, data=payload) # getting data from 2nd url
        print("Response from URL2 received. Status:", response2.status_code)
            
        #check status if ok
        print("Parsing API responses...") 
         
        response1.raise_for_status()
        res1 = response1.json()
        

        if res1['status'] is True:

            #to get expiry date, registration code, email and password from 1st API URL
                
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
            
            
            #API parsin usrl2
            response2.raise_for_status()
            res2 = response2.json()

            #to get no. of employees, devices and users to allow as per license
            templates_api = res2['result'][0]['param_value']
            
            # Save or process the data as required

            request.session['license_data'] =  {
                "expiry_date": expdt,
                "license_key": license_key,
                "registration_code": registcode,
                "name" :nme,
                "email": eml,
                "customer_id": cust_id,
                "password" : passw,
                "database" : dtbs,
                "country_id": cntry_id,
                "country_name":country_name,
                "allowed_templates" : templates_api
            }

            # param_data = {
            #     "expiry_date": time,
            #     "license_key": license_key,
            #     "registration_code": registcode,
            #     "name" :nme,
            #     "email": eml,
            #     "customer_id": cust_id,
            #     "password" : passw,
            #     "database" : dtbs
            # }
            # print(param_data)

            return JsonResponse({"status": "success", "message": "Data processed and stored."})
        
        else:
            print("api status false")
            return JsonResponse({"status": "Failed", "message": "Data not process"})

    except Exception as e:
        print("Error occurred:", str(e))  # Log error details
        return JsonResponse({"status": "error", "message": str(e)}, status=500)