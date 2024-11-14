from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import UserProfile

class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label='Usuario',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese su usuario'})
    )
    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese su contraseña'})
    )

class RegistroForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese su email'})
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for fieldname in ['username', 'password1', 'password2']:
            self.fields[fieldname].widget.attrs = {'class': 'form-control'} 

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'style': 'height: 45px'
    }))

    class Meta:
        model = User
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'style': 'height: 45px'
            })
        }

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['telefono', 'direccion_envio', 'ciudad_envio', 'codigo_postal_envio',
                 'direccion_facturacion', 'ciudad_facturacion', 'codigo_postal_facturacion']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control',
                'style': 'height: 45px'
            }) 