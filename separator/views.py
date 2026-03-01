import os
from django.shortcuts import render
from django.http import JsonResponse, FileResponse
from .forms import AudioUploadForm
from .models import AudioSeparation
from django.conf import settings
from pydub import AudioSegment

# IMPORTANTE: Importando a tarefa do Celery que criamos
from .tasks import process_audio_task

AudioSegment.converter = r"C:\ffmpeg\bin\ffmpeg.exe"

def upload_audio(request):
    if request.method == 'POST':
        form = AudioUploadForm(request.POST, request.FILES)
        if form.is_valid():
            separation = form.save()
            
            # O GATILHO: Dispara a música para a fila do Celery trabalhar em segundo plano!
            process_audio_task.delay(separation.id)
            
            # Devolvemos um JSON de sucesso com os dados do áudio
            return JsonResponse({
                'success': True,
                'separation_id': separation.id,
                'title': separation.title,
                'status': separation.get_status_display()
            })
        else:
            # Se houver erro de validação (ex: arquivo não suportado)
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
            
    # Se for GET, apenas renderiza a página vazia
    form = AudioUploadForm()
    return render(request, 'separator/upload.html', {'form': form})


def check_status(request, separation_id):
    try:
        track = AudioSeparation.objects.get(id=separation_id)
        data = {
            'status': track.status,
            'status_display': track.get_status_display()
        }
        
        if track.status == 'COMPLETED':
            data['files'] = {
                'vocals': track.vocals_file.url if track.vocals_file else '',
                'drums': track.drums_file.url if track.drums_file else '',
                'bass': track.bass_file.url if track.bass_file else '',
                # ADICIONADOS PARA O MODELO 6S
                'guitar': track.guitar_file.url if track.guitar_file else '',
                'piano': track.piano_file.url if track.piano_file else '',
                'other': track.other_file.url if track.other_file else '',
            }
        return JsonResponse(data)
    except AudioSeparation.DoesNotExist:
        return JsonResponse({'error': 'Não encontrado'}, status=404)


def mix_and_download(request, separation_id):
    """ View que recebe as faixas desejadas, junta tudo e faz o download """
    if request.method == 'POST':
        track = AudioSeparation.objects.get(id=separation_id)
        
        # Pega as faixas que o usuário marcou no frontend
        selected_tracks = request.POST.getlist('tracks') # ex: ['drums', 'bass']
        
        if not selected_tracks:
            return JsonResponse({'error': 'Nenhuma faixa selecionada'}, status=400)

        # Mapeia as opções para os caminhos reais dos arquivos
        file_map = {
            'vocals': track.vocals_file.path if track.vocals_file else None,
            'drums': track.drums_file.path if track.drums_file else None,
            'bass': track.bass_file.path if track.bass_file else None,
            'guitar': track.guitar_file.path if track.guitar_file else None,
            'piano': track.piano_file.path if track.piano_file else None,
            'other': track.other_file.path if track.other_file else None,
        }

        mixed_audio = None
        
        # Junta (faz o overlay) de cada faixa selecionada
        for t in selected_tracks:
            path = file_map.get(t)
            if path and os.path.exists(path):
                segment = AudioSegment.from_file(path)
                if mixed_audio is None:
                    mixed_audio = segment
                else:
                    mixed_audio = mixed_audio.overlay(segment)

        if mixed_audio:
            # Salva o arquivo final temporariamente
            output_filename = f"custom_mix_{track.title}.mp3"
            output_path = os.path.join(settings.MEDIA_ROOT, 'uploads', output_filename)
            mixed_audio.export(output_path, format="mp3", bitrate="192k")
            
            # Retorna o arquivo para download
            return FileResponse(open(output_path, 'rb'), as_attachment=True, filename=output_filename)

    return JsonResponse({'error': 'Método inválido'}, status=400)