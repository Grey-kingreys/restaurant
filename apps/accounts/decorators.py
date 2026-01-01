from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps

def role_required(*roles):
    """
    Décorateur pour restreindre l'accès aux vues selon les rôles
    Usage: @role_required('Rtable', 'Rserveur')
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.error(request, "Vous devez être connecté")
                return redirect('accounts:login')
            
            if request.user.role not in roles:
                messages.error(request, "Accès non autorisé")
                return redirect('accounts:dashboard')
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def table_required(view_func):
    return role_required('Rtable')(view_func)

def serveur_required(view_func):
    return role_required('Rserveur')(view_func)

def cuisinier_required(view_func):
    return role_required('Rcuisinier')(view_func)

def comptable_required(view_func):
    return role_required('Rcomptable')(view_func)

def admin_required(view_func):
    return role_required('Radmin')(view_func)