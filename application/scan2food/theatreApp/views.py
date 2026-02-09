from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.shortcuts import redirect, render

class CustomLoginView(LoginView):
    template_name = 'theatre/login.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            # Check user type and redirect accordingly
            user_group = request.user.groups.first()
            
            # If user is service provider, redirect to admin portal
            if user_group and user_group.name == 'service_provider':
                return redirect('admin-portal:index')
            
            # If user is superuser/admin, redirect to admin portal
            if request.user.is_superuser:
                return redirect('admin-portal:index')
            
            # Otherwise, redirect to theatre dashboard
            return redirect("theatre:all-seats")
        return super().dispatch(request, *args, **kwargs)

    def form_invalid(self, form):
        messages.error(self.request, "Invalid username or password")
        return super().form_invalid(form)
    
    def get_success_url(self):
        """Redirect after successful login based on user type"""
        user_group = self.request.user.groups.first()
        
        # If user is service provider, redirect to admin portal
        if user_group and user_group.name == 'service_provider':
            return '/admin-portal/'
        
        # If user is superuser/admin, redirect to admin portal
        if self.request.user.is_superuser:
            return '/admin-portal/'
        
        # Otherwise, redirect to theatre dashboard
        return '/theatre/'


def custom_404_view(request, exception):
    return render(request, "website/404.html", status=404)

