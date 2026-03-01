from django.urls import path
from . import views

urlpatterns = [
    path('', views.upload_audio, name='upload_audio'),
    path('status/<int:separation_id>/', views.check_status, name='check_status'),
    path('mix/<int:separation_id>/', views.mix_and_download, name='mix_and_download'),
]