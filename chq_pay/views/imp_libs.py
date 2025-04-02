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
from random import randrange #for random range
from django.core.exceptions import ValidationError

#for csv and pdfs
import pandas as pd
import openpyxl
from openpyxl.utils import get_column_letter
from openpyxl.styles import Font, PatternFill
from openpyxl.worksheet.table import Table, TableStyleInfo #operations for exporting sample in excel

#for excel sheets
import csv
import xlwt
import openpyxl


from django.contrib.auth.hashers import make_password

#for language change
from django.conf.global_settings import LANGUAGES
from django.utils import translation
from django.utils.translation import activate, gettext_lazy as _



import logging

# Set up logging
logger = logging.getLogger(__name__)


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



url1 = f"{api_call_site}/index.php?route=api/license_product_3/get_detail"
url2 = f"{api_call_site}/index.php?route=api/license_product_3/lic_parameter"

# global variable for site for apis




#to write he database setting ton the settings file
def update_settings_file(database_name, reg_code):
    base_dir = Path(__file__).resolve().parent.parent.parent
    proj_folder = os.path.join(base_dir, 'ChequePay')
    settings_file_path = os.path.join(proj_folder, 'db_config.py')

    # Read the file and check if the database already exists
    with open(settings_file_path, 'r') as f:
        lines = f.readlines()

    database_exists = any(f"'{reg_code}':" in line for line in lines)

    if database_exists:
        logger.info(f"Settings for {reg_code} already exist. No changes made.")
        print(f"Settings for {reg_code} already exist. No changes made.")
        return False  # Indicate no changes were made

    # Update the file only if the database setting does not exist
    with open(settings_file_path, 'r+') as f:
        f.seek(0)
        for line in lines:
            f.write(line)
            if line.startswith('DATABASES = {'):
                f.write(f"    '{reg_code}': {{\n")
                f.write(f"        'ENGINE': 'django.db.backends.sqlite3',\n")
                f.write(f"        'NAME': BASE_DIR/'{database_name}',\n")
                f.write(f"    }},\n")
        f.truncate()
    logger.info(f"Settings for {reg_code} added successfully.")
    print(f"Settings for {reg_code} added successfully.")
    return True  # Indicate changes were made



@csrf_exempt
def check_reg_update_sett(request):
    logger.info("View function check_reg_update_sett called.")

    try:
        if request.method == "GET":
            logger.info("Received GET request. Extracting reg_code from URL parameters...")
            reg_code = request.GET.get('reg_code', '').strip()
            logger.info(" reg_code extracted from GET: %s", reg_code)
        elif request.method == "POST":
            logger.info("Received POST request. Parsing JSON body...")
            try:
                data = json.loads(request.body)
                reg_code = data.get('reg_code', '').strip()
                logger.info("reg_code extracted from POST: %s", reg_code)
            except json.JSONDecodeError:
                logger.info("Invalid JSON format in request body.")
                return JsonResponse({"status": "error", "message": "Invalid JSON format"}, status=400)
        else:
            logger.info("Invalid request method: %s", request.method)
            return JsonResponse({"status": "error", "message": "Invalid request method"}, status=405)


        if not reg_code or len(reg_code) < 4:
            logger.warning("Invalid registration code: %s", reg_code)
            return JsonResponse({"status": "error", "message": "Invalid registration code"}, status=400)

        # Fetch data from the APIs
        logger.info("Preparing API calls...")
        
        payload = {"lic_code": reg_code, "master_product_id": "865"}
        logger.info("Payload prepared: %s", payload)

        logger.info("Making API call to URL1...")
        response1 = requests.post(url1, data=payload)
        logger.info("Response from URL1: Status %d", response1.status_code)        

        # Parse responses
        logger.info("Parsing responses...")
        response1.raise_for_status()
        res1 = response1.json()
        logger.info("Response from URL1 parsed: %s", res1)

        
        if res1['status'] is True:
            logger.info("API status is True. Extracting data...")

            logger.info("Updating settings file...")
            settings_updated = update_settings_file(f"chqpaydb_{reg_code}.sqlite3", reg_code)

            if not settings_updated:
                logger.info(f"No changes made to settings. Skipping reload.")
                return JsonResponse({"status": "success", "message": "Settings already exist. No reload required."})

            logger.info("Settings file updated successfully.")
            return JsonResponse({"status": "success", "message": "Data processed and stored."})
        else:
            logger.warning("API status is False.")
            return JsonResponse({"status": "Failed", "message": "Data not processed"})

    except Exception as e:
        logger.error("Exception occurred: %s", e)
        return JsonResponse({"status": "error", "message": str(e)}, status=500)
    




#Created By Faraz Ahmed Raj.
def set_language(request):
    """
    View function to set the user's language preference
    """
    if request.method == 'POST' and 'language' in request.POST:
        language = request.POST['language']
        if language in dict(settings.LANGUAGES):
            translation.activate(language)
            response = redirect(request.META.get('HTTP_REFERER', '/'))
            response.set_cookie(settings.LANGUAGE_COOKIE_NAME, language)

           
            return response
    return redirect(request.META.get('HTTP_REFERER', '/'))



