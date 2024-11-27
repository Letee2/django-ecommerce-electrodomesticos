from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from .forms import LoginForm, RegistroForm, UserUpdateForm, ProfileUpdateForm
from .models import UserProfile
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json

def registro(request):
    if request.user.is_authenticated:
        return redirect('home')
        
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                user = form.save()
                user.backend = 'users.backends.EmailOrUsernameModelBackend'
                login(request, user)
                messages.success(request, f'¡Bienvenido {user.username}! Tu cuenta ha sido creada exitosamente.')
                return redirect('home')
        else:
            for error in form.errors.values():
                messages.error(request, error[0])
    else:
        form = RegistroForm()
    return render(request, 'users/registro.html', {'form': form})

def iniciar_sesion(request):
    if request.user.is_authenticated:
        return redirect('home')
        
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'¡Bienvenido de nuevo, {user.username}!')
                next_url = request.GET.get('next', 'home')
                return redirect(next_url)
        messages.error(request, 'Usuario o contraseña incorrectos')
    else:
        form = LoginForm()
    return render(request, 'users/login.html', {'form': form})

@login_required
def cerrar_sesion(request):
    logout(request)
    messages.info(request, '¡Has cerrado sesión correctamente!')
    return redirect('home')

@login_required
def profile(request):
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, instance=request.user.userprofile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Tu perfil ha sido actualizado.')
            return redirect('profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.userprofile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form
    }
    return render(request, 'users/profile.html', context)

@login_required
@require_POST
def update_profile_ajax(request):
    try:
        data = json.loads(request.body)
        profile = request.user.userprofile
        
        # Actualizar campos del perfil
        profile.direccion_envio = data.get('direccion_envio', profile.direccion_envio)
        profile.ciudad_envio = data.get('ciudad_envio', profile.ciudad_envio)
        profile.codigo_postal_envio = data.get('codigo_postal_envio', profile.codigo_postal_envio)
        profile.telefono = data.get('telefono', profile.telefono)
        profile.save()
        
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required
def update_profile(request):
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, instance=request.user.userprofile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile = profile_form.save(commit=False)
            
            # Si misma_direccion está marcado, copiar datos de envío a facturación
            if profile.misma_direccion:
                profile.direccion_facturacion = profile.direccion_envio
                profile.ciudad_facturacion = profile.ciudad_envio
                profile.codigo_postal_facturacion = profile.codigo_postal_envio
            
            profile.save()
            messages.success(request, 'Tu perfil ha sido actualizado.')
            return redirect('profile')
