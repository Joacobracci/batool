from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.db import models
from django.db.models import F
from .forms import VideoUploadForm, StepForm
from .models import Video, Step
from django.http import JsonResponse

# Create your views here.
def index(request):
    if request.user.is_authenticated:
        # Aquí puedes añadir cualquier contexto adicional para usuarios autenticados
        context = {
            'username': request.user.username,
            'last_login': request.user.last_login,
        }
        return render(request, 'video_handler/home.html', context)
    return render(request, 'video_handler/index.html')

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Cuenta creada exitosamente para {username}!')
            return redirect('video_handler:login')
    else:
        form = UserCreationForm()
    
    return render(request, 'video_handler/signup.html', {'form': form})

def login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            messages.success(request, f'¡Bienvenido {user.username}!')
            return redirect('video_handler:index')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos')
    else:
        form = AuthenticationForm()
    
    return render(request, 'video_handler/login.html', {'form': form})

def logout(request):
    auth_logout(request)
    messages.success(request, '¡Has cerrado sesión exitosamente!')
    return redirect('video_handler:index')

@login_required
def profile(request):
    return render(request, 'video_handler/profile.html')

@login_required
def upload_video(request):
    if request.method == 'POST':
        form = VideoUploadForm(request.POST, request.FILES)
        if form.is_valid():
            video = form.save(commit=False)
            video.user = request.user
            video.save()
            messages.success(request, '¡Video subido exitosamente!')
            return redirect('video_handler:my_videos')
    else:
        form = VideoUploadForm()
    return render(request, 'video_handler/upload_video.html', {'form': form})

@login_required
def my_videos(request):
    videos = Video.objects.filter(user=request.user).order_by('-uploaded_at')
    return render(request, 'video_handler/my_videos.html', {'videos': videos})

@login_required
def video_detail(request, video_id):
    video = get_object_or_404(Video, id=video_id, user=request.user)
    steps = video.steps.all()  # Obtiene todos los pasos ordenados por 'order'
    
    if request.method == 'POST':
        form = StepForm(request.POST)
        if form.is_valid():
            step = form.save(commit=False)
            step.video = video
            step.order = steps.count() + 1  # Asigna el siguiente orden
            step.save()
            messages.success(request, 'Paso añadido exitosamente!')
            return redirect('video_handler:video_detail', video_id=video.id)
    else:
        form = StepForm()
    
    context = {
        'video': video,
        'steps': steps,
        'form': form,
    }
    return render(request, 'video_handler/video_detail.html', context)

@login_required
def edit_step(request, step_id):
    step = get_object_or_404(Step, id=step_id, video__user=request.user)
    if request.method == 'POST':
        form = StepForm(request.POST, instance=step)
        if form.is_valid():
            form.save()
            messages.success(request, '¡Paso actualizado exitosamente!')
            return redirect('video_handler:video_detail', video_id=step.video.id)
    else:
        form = StepForm(instance=step)
    
    return render(request, 'video_handler/edit_step.html', {
        'form': form,
        'step': step
    })

@login_required
def delete_step(request, step_id):
    step = get_object_or_404(Step, id=step_id, video__user=request.user)
    video_id = step.video.id
    
    if request.method == 'POST':
        # Reordenar los pasos restantes
        Step.objects.filter(
            video=step.video,
            order__gt=step.order
        ).update(order=F('order') - 1)
        
        step.delete()
        messages.success(request, '¡Paso eliminado exitosamente!')
        return redirect('video_handler:video_detail', video_id=video_id)
    
    return render(request, 'video_handler/confirm_delete_step.html', {'step': step})


