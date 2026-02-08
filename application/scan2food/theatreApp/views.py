from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.shortcuts import redirect, render

class CustomLoginView(LoginView):
    template_name = 'theatre/login.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("theatre:all-seats")
        return super().dispatch(request, *args, **kwargs)

    def form_invalid(self, form):
        messages.error(self.request, "Invalid username or password")
        return super().form_invalid(form)


def custom_404_view(request, exception):
    return render(request, "website/404.html", status=404)

