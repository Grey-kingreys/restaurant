from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['login', 'role', 'actif', 'date_creation']
    list_filter = ['role', 'actif']
    search_fields = ['login']
    
    fieldsets = (
        (None, {'fields': ('login', 'password')}),
        ('Informations', {'fields': ('role', 'actif')}),
        ('Permissions', {'fields': ('is_staff', 'is_superuser')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('login', 'role', 'password1', 'password2', 'actif'),
        }),
    )
    
    ordering = ['login']