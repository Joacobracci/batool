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
            'title', 'description', 'step_type',
            'start_time', 'end_time', 'is_start_event',
            'is_end_event', 'gateway_type'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'start_time': forms.NumberInput(attrs={'step': '0.1'}),
            'end_time': forms.NumberInput(attrs={'step': '0.1'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Inicializar el campo gateway_type como visible/oculto según step_type
        if self.instance and self.instance.step_type == 'gateway':
            self.fields['gateway_type'].widget.attrs['style'] = 'display: block;'
        else:
            self.fields['gateway_type'].widget.attrs['style'] = 'display: none;' 