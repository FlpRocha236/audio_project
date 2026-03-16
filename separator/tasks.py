import os
import sys
import subprocess
from celery import shared_task
from django.conf import settings
from .models import AudioSeparation

def download_youtube_audio(youtube_url: str, output_path: str) -> str:
    command = [
        sys.executable, "-m", "yt_dlp",
        "--extract-audio",
        "--audio-format", "mp3",
        "--audio-quality", "0",
        "--output", output_path,
        "--no-playlist",
        "--extractor-args", "youtube:player_client=android", # Bypass para o bloqueio de bot do YouTube
        youtube_url,
    ]
    subprocess.run(command, check=True)
    return output_path

@shared_task
def process_audio_task(separation_id):
    try:
        track = AudioSeparation.objects.get(id=separation_id)
        track.status = 'PROCESSING'
        track.save()

        if track.youtube_url:
            originals_dir = os.path.join(settings.MEDIA_ROOT, 'uploads/originals')
            os.makedirs(originals_dir, exist_ok=True)

            safe_title = "".join(
                c for c in (track.title or f"youtube_{separation_id}")
                if c.isalnum() or c in (' ', '-', '_')
            ).strip().replace(' ', '_')

            output_path = os.path.join(originals_dir, f"{safe_title}.mp3")
            download_youtube_audio(track.youtube_url, output_path)

            relative_path = os.path.relpath(output_path, settings.MEDIA_ROOT)
            track.original_audio.name = relative_path
            track.save()

        input_path = track.original_audio.path
        output_dir = os.path.join(settings.MEDIA_ROOT, 'uploads/separated')
        os.makedirs(output_dir, exist_ok=True)

        # Usa a API Python do demucs diretamente — evita problemas de PATH
        from demucs.separate import main as demucs_main
        
        # --- MODO SOBREVIVÊNCIA PARA GUITARRISTAS (6 FAIXAS, MÍNIMO DE RAM) ---
        sys.argv = [
            "demucs",
            "-n", "htdemucs_6s",  # OBRIGATÓRIO manter este para ter a Guitarra
            "--out", output_dir,
            "--segment", "1",     # Fatias minúsculas de 1 segundo (Lento, mas salva muita RAM)
            "--overlap", "0.1",   # Reduz a sobreposição na memória
            "-j", "1",            # Força usar apenas 1 processo/thread
            input_path
        ]
        demucs_main()

        base_filename = os.path.splitext(os.path.basename(input_path))[0]
        demucs_folder = f"uploads/separated/htdemucs_6s/{base_filename}"

        track.vocals_file.name = f"{demucs_folder}/vocals.wav"
        track.drums_file.name  = f"{demucs_folder}/drums.wav"
        track.bass_file.name   = f"{demucs_folder}/bass.wav"
        track.guitar_file.name = f"{demucs_folder}/guitar.wav"
        track.piano_file.name  = f"{demucs_folder}/piano.wav"
        track.other_file.name  = f"{demucs_folder}/other.wav"

        track.status = 'COMPLETED'
        track.save()

    except Exception as e:
        track = AudioSeparation.objects.get(id=separation_id)
        track.status = 'FAILED'
        track.error_message = str(e) # Salva o erro no banco para o Angular mostrar
        track.save()
        print(f"Erro crítico ao processar o áudio: {e}")