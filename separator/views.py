import os
import json
from django.shortcuts import render
from django.http import JsonResponse, FileResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
from pydub import AudioSegment

from .forms import AudioUploadForm
from .models import AudioSeparation
from .tasks import process_audio_task

# FFmpeg via settings (não mais hardcoded)
if hasattr(settings, 'FFMPEG_PATH') and settings.FFMPEG_PATH != 'ffmpeg':
    AudioSegment.converter = settings.FFMPEG_PATH


@csrf_exempt
@require_http_methods(["GET", "POST"])
def upload_audio(request):
    """
    POST — recebe o arquivo de áudio (multipart/form-data) e dispara o Celery
    GET  — retorna status 200 para healthcheck
    """
    if request.method == 'POST':
        form = AudioUploadForm(request.POST, request.FILES)
        if form.is_valid():
            separation = form.save()
            process_audio_task.delay(separation.id)

            return JsonResponse({
                'success': True,
                'separation_id': separation.id,
                'title': separation.title,
                'status': separation.status,
                'status_display': separation.get_status_display(),
            }, status=201)

        return JsonResponse({
            'success': False,
            'errors': form.errors
        }, status=400)

    # GET — healthcheck
    return JsonResponse({'status': 'Audio Splitter API online'})


@require_http_methods(["GET"])
def check_status(request, separation_id):
    """
    GET — retorna o status atual do processamento.
    Quando COMPLETED, inclui as URLs de cada stem e dos arquivos MIDI.
    """
    try:
        track = AudioSeparation.objects.get(id=separation_id)
    except AudioSeparation.DoesNotExist:
        return JsonResponse({'error': 'Separação não encontrada'}, status=404)

    data = {
        'separation_id': track.id,
        'title': track.title,
        'status': track.status,
        'status_display': track.get_status_display(),
    }

    if track.status == 'COMPLETED':
        base = request.build_absolute_uri('/')[:-1]  # ex: https://api.railway.app

        def url(field):
            return base + field.url if field else None

        data['stems'] = {
            'vocals': url(track.vocals_file),
            'drums':  url(track.drums_file),
            'bass':   url(track.bass_file),
            'guitar': url(track.guitar_file),
            'piano':  url(track.piano_file),
            'other':  url(track.other_file),
        }

    if track.status == 'FAILED':
        data['error_message'] = 'Ocorreu um erro durante o processamento.'

    return JsonResponse(data)


@csrf_exempt
@require_http_methods(["POST"])
def mix_and_download(request, separation_id):
    """
    POST — recebe lista de stems via JSON e retorna o arquivo mixado para download.
    Body: { "tracks": ["drums", "bass", "guitar"] }
    """
    try:
        track = AudioSeparation.objects.get(id=separation_id)
    except AudioSeparation.DoesNotExist:
        return JsonResponse({'error': 'Separação não encontrada'}, status=404)

    if track.status != 'COMPLETED':
        return JsonResponse({'error': 'Processamento ainda não concluído'}, status=400)

    # Aceita tanto JSON quanto form-data
    try:
        body = json.loads(request.body)
        selected_tracks = body.get('tracks', [])
    except (json.JSONDecodeError, AttributeError):
        selected_tracks = request.POST.getlist('tracks')

    if not selected_tracks:
        return JsonResponse({'error': 'Nenhuma faixa selecionada'}, status=400)

    file_map = {
        'vocals': track.vocals_file.path if track.vocals_file else None,
        'drums':  track.drums_file.path  if track.drums_file  else None,
        'bass':   track.bass_file.path   if track.bass_file   else None,
        'guitar': track.guitar_file.path if track.guitar_file else None,
        'piano':  track.piano_file.path  if track.piano_file  else None,
        'other':  track.other_file.path  if track.other_file  else None,
    }

    mixed_audio = None
    for stem in selected_tracks:
        path = file_map.get(stem)
        if path and os.path.exists(path):
            segment = AudioSegment.from_file(path)
            mixed_audio = segment if mixed_audio is None else mixed_audio.overlay(segment)

    if not mixed_audio:
        return JsonResponse({'error': 'Nenhum arquivo de faixa encontrado'}, status=400)

    # Salva o mix temporariamente e retorna para download
    safe_title = "".join(c for c in track.title if c.isalnum() or c in (' ', '-', '_')).strip()
    output_filename = f"mix_{safe_title or track.id}.mp3"
    output_path = os.path.join(settings.MEDIA_ROOT, 'uploads', output_filename)

    mixed_audio.export(output_path, format='mp3', bitrate='192k')

    response = FileResponse(
        open(output_path, 'rb'),
        as_attachment=True,
        filename=output_filename,
        content_type='audio/mpeg'
    )
    return response