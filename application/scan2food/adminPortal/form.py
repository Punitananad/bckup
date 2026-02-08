from django import forms
from .models import PaymentGateway, Detail, Documents, bankDetails, GSTDetails, Query

class PaymentGatewayForm(forms.ModelForm):
    class Meta:
        model = PaymentGateway
        fields = ['name', 'gateway_key', 'gateway_secret']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'gateway_key': forms.TextInput(attrs={'class': 'form-control'}),
            'gateway_secret': forms.TextInput(attrs={'class': 'form-control'}),
        }

class DetailForm(forms.ModelForm):
    class Meta:
        model = Detail
        exclude = ['theatre', 'start_date', 'logo', 'expire_date', 'is_active', 'break_start_time', 'scaning_service']  # exclude auto fields

    def __init__(self, *args, **kwargs):
        super(DetailForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

class BankDetailsForm(forms.ModelForm):
    class Meta:
        model = bankDetails
        exclude = ['theatre']

    def __init__(self, *args, **kwargs):
        super(BankDetailsForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

class GSTDetailsForm(forms.ModelForm):
    class Meta:
        model = GSTDetails
        exclude = ['theatre']

    def __init__(self, *args, **kwargs):
        super(GSTDetailsForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'



class ImageUploadform(forms.Form):
    file = forms.FileField(
        label='Uploa Food Image',
        widget=forms.FileInput(attrs={'class': 'form-control mb-3'})
    )

class DocumentForm(forms.ModelForm):
    class Meta:
        model = Documents
        fields = ['document_name', 'document']
        widgets = {
            'document_name': forms.TextInput(attrs={'class': 'form-control'}),
            'document': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

class QueryForm(forms.ModelForm):
    class Meta:
        model = Query
        fields = ["name", "email", "phone", "place", "description"]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'name',
                'placeholder': 'Your Name',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'id': 'email',
                'placeholder': 'Your Email',
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'contactNo',
                'placeholder': 'Your Contact Number',
            }),
            'place': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'place',
                'placeholder': 'Your Place',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'id': 'message',
                'placeholder': 'Write your Question Here',
                'style': 'height: 100px',
            }),
        }