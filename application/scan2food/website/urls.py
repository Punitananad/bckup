from django.urls import path
from . import views

app_name = "website"
urlpatterns = [
    path('', views.index, name='index'),
    path('terms-and-condition', views.terms_and_conditions, name='terms-and-condition'),
    path('policy', views.policy, name='policy'),
    path('oc', views.orderconformation, name='oc')
]