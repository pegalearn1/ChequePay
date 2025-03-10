"""
URL configuration for ChequePay project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from chq_pay.views import base_views, authentic_views, cheque_views, bank_views, payee_views, currency_views, company_views, cheque_issue, imp_libs, user_views, report_views
from django.contrib.auth.views import LogoutView
from chq_pay.forms import BankForm, CurrencyForm, PayeeForm
from chq_pay.views.wizard_views import AppSetupWizard

urlpatterns = [
    #base/home urls
    path('', base_views.home, name = "home"),
    path('base/', base_views.base_temp, name = "base"),
    path('index/', base_views.index, name = "index"),
    path('profile/', base_views.profile, name = "profile"),
  
    #login/register urls
    path("logout/", authentic_views.user_logout, name="logout"),
    path('login/', authentic_views.user_login, name = "login"),
    path('check_reg_update_sett/', imp_libs.check_reg_update_sett, name = "check_reg_update_sett"),

    
    #User Views
    path('add_user/', user_views.add_user, name='add_user'),
    path('users_list/', user_views.users_list, name = "users_list"),
    path('edit_user/', user_views.edit_user, name='edit_user'),
    path('delete_user/<int:user_id>/', user_views.delete_user, name='delete_user'),

    
    
    #company urls
    path('add_company/', company_views.add_company, name='add_company'),
    path('company_list/', company_views.company_list, name = "company_list"),
    path('edit_company/', company_views.edit_company, name='edit_company'),
    path('delete_company/<int:company_id>/', company_views.delete_company, name='delete_company'),
    path('current_company', company_views.current_company, name='current_company'),
    
    
    
    #bank urls
    path('add-bank/', bank_views.add_bank, name='add_bank'),
    path('bank_list/', bank_views.bank_list, name = "bank_list"),
    path('edit-bank/', bank_views.edit_bank, name='edit_bank'),
    path('delete_bank/<int:bank_id>/', bank_views.delete_bank, name='delete_bank'),
    path('excel_upload_bank/validate/', bank_views.validate_excel_bank, name='validate_excel_bank'),
    path('excel_upload_bank/save/', bank_views.save_valid_data_bank, name='save_valid_data_bank'),
    path('download_sample_bank/', bank_views.download_sample_bank, name='download_sample_bank'),

    #payee urls
    path('add_payee/', payee_views.add_payee, name='add_payee'),
    path('payee_list/', payee_views.payee_list, name = "payee_list"),
    path('edit_payee/', payee_views.edit_payee, name='edit_payee'),
    path('delete_payee/<int:payee_id>/', payee_views.delete_payee, name='delete_payee'),
    path('excel_upload_payee/validate/', payee_views.validate_excel_payee, name='validate_excel_payee'),
    path('excel_upload_payee/save/', payee_views.save_valid_data_payee, name='save_valid_data_payee'),
    path('download_sample_payee/', payee_views.download_sample_payee, name='download_sample_payee'),


    #currency urls
    path('add_currency/', currency_views.add_currency, name='add_currency'),
    path('currency_list/', currency_views.currency_list, name = "currency_list"),
    path('edit_currency/', currency_views.edit_currency, name='edit_currency'),
    path('delete_currency/<int:currency_id>/', currency_views.delete_currency, name='delete_currency'),
    
    
    #cheque_template_related urls
    path('upload_template/', cheque_views.upload_template, name = "upload_template"),
    path('template_list/', cheque_views.template_list, name = "template_list"),
    path('edit-template/', cheque_views.edit_template, name='edit_template'),
    path('template/<int:template_id>/', cheque_views.template_detail, name='template_detail'),
    path('delete_temp/<int:template_id>/', cheque_views.delete_template, name='delete_template'),
    path('template/<int:template_id>/add-text/', cheque_views.add_text_to_template, name='add_text_to_template'),
    path('reset_text/<int:temp_id>/', cheque_views.reset_text, name='reset_text'),
    path('delete_text/<int:text_id>/<int:temp_id>/', cheque_views.delete_text, name='delete_text'),
    path('template/<int:template_id>/print/', cheque_views.print_cheque, name='print_cheque'),

    #cheque_issue_related urls
    path('cheque_issue/', cheque_issue.cheque_issue, name = "cheque_issue"),
    path('cheque_issue_list/', cheque_issue.cheque_issue_list, name = "cheque_issue_list"),
    path('edit_cheque_issue/', cheque_issue.edit_cheque_issue, name='edit_cheque_issue'),
    path('delete_chequeissue/<int:chequeissue_id>/', cheque_issue.delete_chequeissue, name='delete_chequeissue'),
    path('get_cheque_text', cheque_issue.get_cheque_text, name='get_cheque_text'),
    path('print-cheque/<int:cheque_id>/', cheque_issue.print_cheque, name='print_cheque'),
    path('approval/<int:cheque_id>/', cheque_issue.approval, name='approval'),

    #Reports
    path('reports/', report_views.reports, name='reports'),
    path('reports/export/<str:file_format>/', report_views.export_payee_report, name='export_payee_report'),


    #wizard
     path(
        "setup-wizard/",
        AppSetupWizard.as_view([BankForm, CurrencyForm, PayeeForm]),
        name="setup_wizard",
    ),

    #Language Switcher

    path('set_language/', imp_libs.set_language, name='set_language'),




]
