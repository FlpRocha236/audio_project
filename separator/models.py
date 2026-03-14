from django.db import models


class AudioSeparation(models.Model):
    STATUS_CHOICES = [
        ('PENDING',    'Pendente'),
        ('PROCESSING', 'Processando'),
        ('COMPLETED',  'Concluído'),
        ('FAILED',     'Erro'),
    ]

    # Dados de entrada
    title          = models.CharField(max_length=255, blank=True, verbose_name="Título da Música")
    original_audio = models.FileField(upload_to='uploads/originals/', blank=True, null=True, verbose_name="Arquivo de Áudio")
    youtube_url    = models.URLField(max_length=500, blank=True, null=True, verbose_name="Link do YouTube")

    # Stems gerados pelo Demucs
    vocals_file = models.FileField(upload_to='uploads/separated/', blank=True, null=True)
    drums_file  = models.FileField(upload_to='uploads/separated/', blank=True, null=True)
    bass_file   = models.FileField(upload_to='uploads/separated/', blank=True, null=True)
    guitar_file = models.FileField(upload_to='uploads/separated/', blank=True, null=True)
    piano_file  = models.FileField(upload_to='uploads/separated/', blank=True, null=True)
    other_file  = models.FileField(upload_to='uploads/separated/', blank=True, null=True)

    # Controle de estado
    status     = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title or f"Upload #{self.id}"