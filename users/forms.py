from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Profile

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
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True, label='Nombre')
    last_name = forms.CharField(required=True, label='Apellidos')

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Este email ya está registrado.')
        return email

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
    direccion_envio = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 2,
            'class': 'form-control'
        })
    )
    direccion_facturacion = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 2,
            'class': 'form-control'
        })
    )
    
    class Meta:
        model = Profile
        fields = [
            'telefono',
            'direccion_envio', 'ciudad_envio', 'codigo_postal_envio',
            'direccion_facturacion', 'ciudad_facturacion', 'codigo_postal_facturacion',
            'misma_direccion'
        ]
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if not isinstance(field.widget, (forms.CheckboxInput, forms.Textarea)):
                field.widget.attrs.update({
                    'class': 'form-control',
                    'style': 'height: 32px'
                }) 