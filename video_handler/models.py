from django.db import models
from django.contrib.auth.models import User

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

    video = models.ForeignKey(Video, related_name='steps', on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField()
    step_type = models.CharField(max_length=20, choices=STEP_TYPES, default='task')
    order = models.IntegerField()  # Para mantener el orden de los pasos
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
    
    # Campos adicionales para BPMN
    is_start_event = models.BooleanField(default=False)
    is_end_event = models.BooleanField(default=False)
    gateway_type = models.CharField(
        max_length=20,
        choices=[
            ('exclusive', 'Exclusive'),
            ('parallel', 'Parallel'),
            ('inclusive', 'Inclusive'),
        ],
        null=True,
        blank=True
    )

    class Meta:
        ordering = ['order']
        unique_together = ['video', 'order']

    def __str__(self):
        return f"{self.video.title} - Step {self.order}: {self.title}"

    def save(self, *args, **kwargs):
        if not self.bpmn_id:
            # Genera un ID único para BPMN si no existe
            import uuid
            self.bpmn_id = f"bpmn_{uuid.uuid4().hex[:8]}"
        super().save(*args, **kwargs)
