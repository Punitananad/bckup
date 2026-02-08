from django import forms
from .models import FoodItem, Theatre, Tax, FoodCategory


class FoodItemForm(forms.ModelForm):
    class Meta:
        model = FoodItem
        fields = ['catogary', 'food_type','made_by', 'name', 'price','min_time', 'max_time', 'description', 'priority_number']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'catogary': forms.Select(attrs={'class': 'form-control'}),
            'food_type': forms.Select(attrs={"class": 'form-control'}),
            'made_by': forms.Select(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'min_time': forms.NumberInput(attrs={'class': 'form-control'}),
            'max_time': forms.NumberInput(attrs={'class': 'form-control'}),
            'priority_number': forms.NumberInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': '10', 'cols': '3', 'style': 'height: 10vh'}),
        }

    def __init__(self, *args, **kwargs):
        # accept a theatre as paremeter
        theatre = kwargs.pop('theatre', None)
        super().__init__(*args, **kwargs)
        if theatre:
            # Filter the queryset of the catogary field
            self.fields['catogary'].queryset = FoodCategory.objects.filter(theatre=theatre)

class FoodCategoryForm(forms.ModelForm):
    class Meta:
        model = FoodCategory
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
        }

class UpdateTheatreDetil(forms.ModelForm):
    class Meta:
        model = Theatre
        fields = ['name', 'owner_name', 'address', 'query_number']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'owner_name': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),

            # 'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            # 'notification_numbers': forms.TextInput(attrs={'class': 'form-control'}),
            'query_number': forms.TextInput(attrs={'class': 'form-control'})
        }

class OtpPhoneNumberForm(forms.ModelForm):
    class Meta:
        model = Theatre
        fields = ['otp_phone_number', 'otp_person_name', 'otp']
        widgets = {
            'otp_phone_number': forms.TextInput(attrs={'class': 'form-control', 'dissabled': 'disabled'}),
            'otp_person_name': forms.TextInput(attrs={'class': 'form-control'}),
            'otp': forms.TextInput(attrs={'class': 'form-control'}),
        }    

class AddTax(forms.ModelForm):
    class Meta:
        model = Tax
        fields = ['name', 'percentage']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'percentage': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class SimpleUserProfileForm(forms.Form):
    name = forms.CharField(
        max_length=35,
        label='Name',
        widget=forms.TextInput(attrs={'class': 'form-control mb-3'})
    )
    phone_number = forms.CharField(
        max_length=15,
        label='Phone Number / Login Id',
        widget=forms.NumberInput(attrs={'class': 'form-control mb-3'})
    )
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control mb-3'})
    )
    user_type = forms.CharField(
        label="User Type",
        widget=forms.Select(attrs={'class': 'form-control mb-3'})
    )

class SignUp(forms.Form):
    theatre_name = forms.CharField(
        max_length=100,
        label='Theatre Name',
        widget=forms.TextInput(attrs={'class': 'form-control mb-3'})
    )
    owner_name = forms.CharField(
        max_length=100,
        label='Owner Name',
        widget=forms.TextInput(attrs={'class': 'form-control mb-3'})
    )
    phone_number = forms.CharField(
        max_length=15,
        label='Phone Number',
        widget=forms.NumberInput(attrs={'class': 'form-control mb-3'})
    )
    email = forms.CharField(
        max_length=50,
        label='Email',
        widget=forms.EmailInput(attrs={'class': 'form-control mb-3'})
    )
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control mb-3'})
    )
