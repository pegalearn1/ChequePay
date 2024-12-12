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
