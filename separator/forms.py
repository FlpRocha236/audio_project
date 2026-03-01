from django import forms
from .models import AudioSeparation

class AudioUploadForm(forms.ModelForm):
    class Meta:
        model = AudioSeparation
        # Vamos pedir apenas o título e o arquivo de áudio para o usuário
        fields = ['title', 'original_audio']
        
        # Opcional: Adicionando classes CSS para facilitar a estilização no HTML depois
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Andy Timmons - Electric Gypsy'}),
            'original_audio': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }