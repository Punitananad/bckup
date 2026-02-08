from django.shortcuts import render, HttpResponse, redirect
from adminPortal.form import QueryForm
from theatre.update_websocket import update_websocket

# Create your views here.
def index(request):
    if request.method == 'POST':
        # form = QueryForm(request.POST)
        # if form.is_valid():
        #     form.save()
        #     phone_number = form.cleaned_data['phone']
        #     update_websocket(message='otp',
        #                      customer_message='✅ *Team Scan2Food* %0A%0Thank you for getting in touch! Our team will be in contact with you very soon.',
        #                      customer_phone=phone_number
        #                      )
        
        # return redirect('website:index')
        return HttpResponse('Method Not Allowed....')
        
    form = QueryForm()
    return render(request, "website/index.html", {'form': form})

def terms_and_conditions(request):
    return render(request, 'website/terms-and-condition.html')

def policy(request):
    return render(request, 'website/policy.html')

def orderconformation(request):
    return render(request, 'website/orderconfirmation.html')