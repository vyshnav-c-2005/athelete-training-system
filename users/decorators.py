from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect

def get_role_redirect(user):
    """
    Helper to return the dashboard URL name based on user role.
    """
    if user.is_authenticated and hasattr(user, 'userprofile'):
        if user.userprofile.role == 'Coach':
            return 'coach_dashboard'
        elif user.userprofile.role == 'Athlete':
            return 'dashboard'
    return 'login'

def athlete_required(view_func):
    def wrapper_func(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        if hasattr(request.user, 'userprofile') and request.user.userprofile.role == 'Athlete':
            return view_func(request, *args, **kwargs)
        
        # If not athlete (and authenticated), redirect to coach dashboard if coach
        if hasattr(request.user, 'userprofile') and request.user.userprofile.role == 'Coach':
            return redirect('coach_dashboard')
            
        return redirect('login')
    return wrapper_func

def coach_required(view_func):
    def wrapper_func(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
            
        if hasattr(request.user, 'userprofile') and request.user.userprofile.role == 'Coach':
            return view_func(request, *args, **kwargs)
            
        # If not coach (and authenticated), redirect to athlete dashboard
        return redirect('dashboard')
    return wrapper_func
