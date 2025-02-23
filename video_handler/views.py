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
from .models import Video, Step, BPMNDiagram
from django.http import JsonResponse
from django.core.serializers import serialize
import json
import xml.etree.ElementTree as ET

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
            try:
                video = form.save(commit=False)
                video.user = request.user
                video.save()
                messages.success(request, 'Video subido exitosamente.')
                return redirect('video_handler:my_videos')
            except Exception as e:
                messages.error(request, f'Error al subir el video: {str(e)}')
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
    video_url = video.get_file_url()
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
        'video_url': video_url,
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

@login_required
def reorder_step(request, step_id, direction):
    step = get_object_or_404(Step, id=step_id, video__user=request.user)
    
    if direction == 'up':
        step.move_up()
    elif direction == 'down':
        step.move_down()
    
    return redirect('video_handler:video_detail', video_id=step.video.id)

@login_required
def save_bpmn(request, video_id):
    if request.method == 'POST':
        video = get_object_or_404(Video, id=video_id, user=request.user)
        xml_content = request.POST.get('xml')
        
        if xml_content:
            diagram = BPMNDiagram.objects.create(
                video=video,
                xml_content=xml_content,
                is_current=True
            )
            return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def load_bpmn(request, video_id):
    video = get_object_or_404(Video, id=video_id, user=request.user)
    diagram = BPMNDiagram.objects.filter(video=video, is_current=True).first()
    
    if diagram:
        return JsonResponse({'xml': diagram.xml_content})
    return JsonResponse({'status': 'no_diagram'})

@login_required
def bpmn_viewer(request, video_id):
    video = get_object_or_404(Video, id=video_id, user=request.user)
    steps = video.steps.all().order_by('order')
    current_diagram = BPMNDiagram.objects.filter(video=video, is_current=True).first()
    
    steps_data = json.loads(serialize('json', steps))
    context = {
        'video': video,
        'steps': json.dumps(steps_data),
        'current_diagram': current_diagram.xml_content if current_diagram else None,
    }
    return render(request, 'video_handler/bpmn_viewer.html', context)

@login_required
def update_steps_from_bpmn(request, video_id):
    if request.method == 'POST':
        video = get_object_or_404(Video, id=video_id, user=request.user)
        try:
            xml_content = request.POST.get('xml')
            
            # Parsear el XML para extraer los pasos
            root = ET.fromstring(xml_content)
            
            # Namespace para BPMN
            ns = {'bpmn2': 'http://www.omg.org/spec/BPMN/20100524/MODEL'}
            
            # Obtener todos los elementos del proceso
            process = root.find('.//bpmn2:process', ns)
            
            # Limpiar pasos existentes
            video.steps.all().delete()
            
            # Crear nuevos pasos
            order = 1
            for element in process:
                tag = element.tag.split('}')[-1]  # Remover namespace
                
                if tag in ['task', 'startEvent', 'endEvent', 'exclusiveGateway', 'parallelGateway', 'inclusiveGateway']:
                    name = element.get('name', '')
                    element_id = element.get('id', '')
                    
                    # Determinar el tipo de paso
                    if tag == 'task':
                        step_type = 'task'
                        gateway_type = None
                        is_start = False
                        is_end = False
                    elif tag == 'startEvent':
                        step_type = 'event'
                        gateway_type = None
                        is_start = True
                        is_end = False
                    elif tag == 'endEvent':
                        step_type = 'event'
                        gateway_type = None
                        is_start = False
                        is_end = True
                    else:  # Gateway
                        step_type = 'gateway'
                        gateway_type = tag.replace('Gateway', '').lower()
                        is_start = False
                        is_end = False
                    
                    # Crear el paso
                    Step.objects.create(
                        video=video,
                        title=name,
                        description=f"Generado desde BPMN - {tag}",
                        step_type=step_type,
                        gateway_type=gateway_type,
                        is_start_event=is_start,
                        is_end_event=is_end,
                        order=order,
                        start_time=0.0,  # Valores por defecto
                        end_time=0.0,
                        bpmn_id=element_id
                    )
                    order += 1
            
            return JsonResponse({'status': 'success'})
            
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
            
    return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)


