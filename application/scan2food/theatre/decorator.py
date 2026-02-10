from django.shortcuts import redirect, HttpResponse
from django.core.exceptions import PermissionDenied
from django.contrib.auth import logout
from django.contrib import messages
from django.utils import timezone


def login_required(view_func):
    def wrapper(request, *args, **kwargs):
        # Check if the user is authenticated
        if request.user.is_authenticated:
            # Check if the user profile and required fields exist
            try:
                user_profile = request.user.userprofile
                
                # Check if user has theatre and active status
                if user_profile.theatre and user_profile.active_status:
                    # Check if theatre has detail and is active
                    if hasattr(user_profile.theatre, 'detail'):
                        theatre_detail = user_profile.theatre.detail
                        if not theatre_detail.is_active:
                            messages.error(request, 'Your payment is Pending')
                            logout(request)
                            return redirect('login')
                    
                    # All conditions are met, proceed to the view
                    return view_func(request, *args, **kwargs)
                else:
                    # Conditions not met, log out the user
                    logout(request)
                    return HttpResponse('permission Denied')

            except AttributeError:
                # Check if user has groups before accessing
                user_group = request.user.groups.first()
                if user_group and user_group.name == 'service_provider':
                    return redirect('admin-portal:index')
                # If user is superuser, redirect to admin
                if request.user.is_superuser:
                    return redirect('/admin/')
                # If userprofile or adminprofile doesn't exist, log out the user
                return HttpResponse('There is some issue - User profile not configured')

        else:
            # User is not authenticated
            return redirect('login')  # Redirect to login page

    return wrapper
