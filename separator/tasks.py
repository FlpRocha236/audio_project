import os
import subprocess
from celery import shared_task
from django.conf import settings
from .models import AudioSeparation

@shared_task
def process_audio_task(separation_id):
    try:
        track = AudioSeparation.objects.get(id=separation_id)
        track.status = 'PROCESSING'
        track.save()

        input_path = track.original_audio.path
        output_dir = os.path.join(settings.MEDIA_ROOT, 'uploads/separated')
        os.makedirs(output_dir, exist_ok=True)

        # ADICIONADO: Forçando o modelo de 6 faixas (htdemucs_6s)
        command = [
            "demucs",
            "-n", "htdemucs_6s",
            "--out", output_dir,
            input_path
        ]
        
        subprocess.run(command, check=True)

        # ADICIONADO: O Demucs 6s cria a pasta com o nome htdemucs_6s
        base_filename = os.path.splitext(os.path.basename(input_path))[0]
        demucs_folder = f"uploads/separated/htdemucs_6s/{base_filename}"

        track.vocals_file.name = f"{demucs_folder}/vocals.wav"
        track.drums_file.name = f"{demucs_folder}/drums.wav"
        track.bass_file.name = f"{demucs_folder}/bass.wav"
        # Mapeando os novos arquivos gerados!
        track.guitar_file.name = f"{demucs_folder}/guitar.wav"
        track.piano_file.name = f"{demucs_folder}/piano.wav"
        track.other_file.name = f"{demucs_folder}/other.wav" # "Other" agora é só sintetizador, barulhos, etc.
        
        track.status = 'COMPLETED'
        track.save()

    except Exception as e:
        track.status = 'FAILED'
        track.save()
        print(f"Erro crítico ao processar o áudio: {e}")