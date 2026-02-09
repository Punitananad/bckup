from django.shortcuts import redirect, HttpResponse
from django.core.exceptions import PermissionDenied
from django.contrib.auth import logout
from django.contrib.auth.models import Group


def login_required(view_func):
    def wrapper(request, *args, **kwargs):
        # Check if the user is authenticated
        if request.user.is_authenticated:
            # Allow superusers to access admin portal
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            
            # Check if the user profile and required fields exist
            try:
                admin_group = Group.objects.filter(name="service_provider").first()
                group = request.user.groups.first()

                if group == admin_group and request.user.adminprofile.active_status == True:
                    # All conditions are met, proceed to the view
                    return view_func(request, *args, **kwargs)
                else:
                    # Conditions not met, log out the user
                    logout(request)
                    # return redirect('permission_denied')  # Define a permission denied page
                    return HttpResponse('permission Denied')

            except AttributeError:
                # If userprofile doesn't exist, log out the user
                logout(request)
                return HttpResponse('permission_denied')

        else:
            # User is not authenticated
            return redirect('login')  # Redirect to login page

    return wrapper
