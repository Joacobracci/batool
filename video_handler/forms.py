from django import forms
from .models import Video, Step

class VideoUploadForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = ['title', 'description', 'file']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class StepForm(forms.ModelForm):
    class Meta:
        model = Step
        fields = [
            'order',
            'title', 
            'description', 
            'step_type',
            'start_time', 
            'end_time', 
            'is_start_event',
            'is_end_event', 
            'gateway_type'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'start_time': forms.NumberInput(attrs={'step': '0.1'}),
            'end_time': forms.NumberInput(attrs={'step': '0.1'}),
            'order': forms.NumberInput(attrs={'class': 'order-input'}),
            'step_type': forms.Select(attrs={'class': 'step-type-select', 'onchange': 'handleStepTypeChange(this)'}),
            'gateway_type': forms.Select(attrs={'class': 'gateway-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['gateway_type'].required = False
        
        # No ocultamos el campo con style, lo manejaremos con CSS
        self.fields['gateway_type'].widget.attrs.update({
            'class': 'gateway-select',
            'data-field-type': 'gateway'
        }) 