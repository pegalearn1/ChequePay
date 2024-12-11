from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import ChqpayUser, Banks
# Register your models here.

@admin.register(ChqpayUser)
class ChqpayUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('profile_picture', 'civil_id', 'privilege_char')}),
    )

@admin.register(Banks)
class BanksAdmin(admin.ModelAdmin):
    list_display = ('id','bank_char','bank_name_e','bank_name_l','tel_no','address')
