import os
import subprocess
from celery import shared_task
from django.conf import settings
from .models import AudioSeparation


def download_youtube_audio(youtube_url: str, output_path: str) -> str:
    """
    Baixa o áudio de um link do YouTube via yt-dlp.
    Retorna o caminho do arquivo baixado.
    """
    command = [
        "yt-dlp",
        "--extract-audio",
        "--audio-format", "mp3",
        "--audio-quality", "0",
        "--output", output_path,
        "--no-playlist",
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

        # Se veio de YouTube, baixa o áudio primeiro
        if track.youtube_url:
            originals_dir = os.path.join(settings.MEDIA_ROOT, 'uploads/originals')
            os.makedirs(originals_dir, exist_ok=True)

            safe_title = "".join(
                c for c in (track.title or f"youtube_{separation_id}")
                if c.isalnum() or c in (' ', '-', '_')
            ).strip().replace(' ', '_')

            output_path = os.path.join(originals_dir, f"{safe_title}.mp3")
            download_youtube_audio(track.youtube_url, output_path)

            # Atualiza o campo original_audio com o arquivo baixado
            relative_path = os.path.relpath(output_path, settings.MEDIA_ROOT)
            track.original_audio.name = relative_path
            track.save()

        input_path = track.original_audio.path
        output_dir = os.path.join(settings.MEDIA_ROOT, 'uploads/separated')
        os.makedirs(output_dir, exist_ok=True)

        command = [
            "demucs",
            "-n", "htdemucs_6s",
            "--out", output_dir,
            input_path
        ]
        subprocess.run(command, check=True)

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
        track.save()
        print(f"Erro crítico ao processar o áudio: {e}")