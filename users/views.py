from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import LoginForm, RegistroForm, UserUpdateForm, ProfileUpdateForm

def iniciar_sesion(request):
    if request.user.is_authenticated:
        return redirect('home')
        
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'¡Bienvenido {user.username}!')
            return redirect('home')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')
    else:
        form = LoginForm()
    return render(request, 'users/login.html', {'form': form})

@login_required
def cerrar_sesion(request):
    logout(request)
    messages.info(request, '¡Has cerrado sesión correctamente!')
    return redirect('home')

def registro(request):
    if request.user.is_authenticated:
        return redirect('home')
        
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, '¡Registro exitoso! Bienvenido.')
            return redirect('home')
    else:
        form = RegistroForm()
    return render(request, 'users/registro.html', {'form': form})

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
