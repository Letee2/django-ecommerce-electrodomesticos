from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile

class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nombre de usuario'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Contraseña'
        })
    )

class RegistroForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-control'
            })

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'})
        }

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['telefono', 'direccion_envio', 'ciudad_envio', 'codigo_postal_envio',
                 'direccion_facturacion', 'ciudad_facturacion', 'codigo_postal_facturacion']
        widgets = {
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion_envio': forms.TextInput(attrs={'class': 'form-control'}),
            'ciudad_envio': forms.TextInput(attrs={'class': 'form-control'}),
            'codigo_postal_envio': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion_facturacion': forms.TextInput(attrs={'class': 'form-control'}),
            'ciudad_facturacion': forms.TextInput(attrs={'class': 'form-control'}),
            'codigo_postal_facturacion': forms.TextInput(attrs={'class': 'form-control'})
        } 