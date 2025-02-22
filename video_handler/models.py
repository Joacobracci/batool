from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class Video(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to='videos/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

class Step(models.Model):
    STEP_TYPES = [
        ('task', 'Task'),
        ('gateway', 'Gateway'),
        ('event', 'Event'),
        ('subprocess', 'Sub Process'),
    ]

    GATEWAY_TYPES = [
        ('exclusive', 'Exclusive'),
        ('parallel', 'Parallel'),
        ('inclusive', 'Inclusive'),
    ]

    video = models.ForeignKey(Video, related_name='steps', on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    step_type = models.CharField(max_length=20, choices=STEP_TYPES, default='task')
    order = models.PositiveIntegerField()
    start_time = models.FloatField(help_text='Tiempo de inicio en el video (segundos)')
    end_time = models.FloatField(help_text='Tiempo de fin en el video (segundos)')
    
    # Campos específicos para BPMN
    bpmn_id = models.CharField(max_length=50, unique=True, help_text='Identificador único para BPMN')
    next_steps = models.ManyToManyField(
        'self',
        blank=True,
        symmetrical=False,
        related_name='previous_steps'
    )
    
    is_start_event = models.BooleanField(default=False)
    is_end_event = models.BooleanField(default=False)
    gateway_type = models.CharField(
        max_length=20,
        choices=GATEWAY_TYPES,
        null=True,
        blank=True
    )

    class Meta:
        ordering = ['order']
        unique_together = ['video', 'order']

    def __str__(self):
        return f"{self.video.title} - Step {self.order}: {self.title}"

    def clean(self):
        if self.is_start_event and self.is_end_event:
            raise ValidationError("Un paso no puede ser evento de inicio y fin simultáneamente")
        
        if self.step_type == 'gateway' and not self.gateway_type:
            raise ValidationError("Los pasos de tipo gateway deben especificar un tipo de gateway")
        
        if self.step_type != 'gateway' and self.gateway_type:
            self.gateway_type = None

    def save(self, *args, **kwargs):
        if not self.bpmn_id:
            import uuid
            self.bpmn_id = f"bpmn_{uuid.uuid4().hex[:8]}"
        
        # Validar el modelo
        self.clean()
        
        # Si es un nuevo paso (sin ID), asignar el último orden + 1
        if not self.id and not self.order:
            last_step = Step.objects.filter(video=self.video).order_by('-order').first()
            self.order = (last_step.order + 1) if last_step else 1
            
        super().save(*args, **kwargs)

    def move_up(self):
        if self.order > 1:
            previous_step = Step.objects.get(video=self.video, order=self.order - 1)
            self.order, previous_step.order = previous_step.order, self.order
            previous_step.save()
            self.save()

    def move_down(self):
        next_step = Step.objects.filter(video=self.video, order=self.order + 1).first()
        if next_step:
            self.order, next_step.order = next_step.order, self.order
            next_step.save()
            self.save()

class BPMNDiagram(models.Model):
    video = models.ForeignKey(Video, related_name='bpmn_diagrams', on_delete=models.CASCADE)
    xml_content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_current = models.BooleanField(default=True)  # Para mantener un historial de versiones

    def __str__(self):
        return f"BPMN for {self.video.title} ({self.created_at})"

    def save(self, *args, **kwargs):
        # Si este es el nuevo diagrama actual, desactivar el anterior
        if self.is_current:
            BPMNDiagram.objects.filter(video=self.video, is_current=True).update(is_current=False)
        super().save(*args, **kwargs)
