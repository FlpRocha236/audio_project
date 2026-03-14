from django.urls import path
from . import views

urlpatterns = [
    path('upload/',                      views.upload_audio,     name='api_upload'),
    path('upload/youtube/',              views.upload_youtube,   name='api_upload_youtube'),
    path('status/<int:separation_id>/',  views.check_status,     name='api_status'),
    path('mix/<int:separation_id>/',     views.mix_and_download, name='api_mix'),
]