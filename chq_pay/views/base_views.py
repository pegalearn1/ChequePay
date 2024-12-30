''' The Project 'Cheque Printer' is solely created by Faraz Ahmed Raj - Python Developer
in 2024-2025.'''

from .imp_libs import *

def home(request):
    return render(request, "home/home.html")

@login_required
def base_temp(request):
    return render(request, "layouts/base.html")

@login_required
def index(request):
    return render(request, "home/index.html")

def icons(request):
    return render(request, "home/icons.html")


