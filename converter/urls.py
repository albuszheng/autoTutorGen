from django.urls import path

from . import views

urlpatterns = [
    path('', views.welcome, name='index'),
    path('about', views.about, name='about'),
    path('upload-success', views.upload_success, name='upload_success'),
    path('upload-failure', views.upload_fail, name='upload_fail'),
    path('processing', views.processing, name='processing'),
    path('upload', views.upload, name='upload'),
    # path('test', views.index, name='index'),
    path('upload/files', views.upload_file, name='file_uploading'),
    path('upload/code', views.code_submitting, name='code_submitting'),
    path('upload/config', views.config_submit, name='config_submit'),
    path('preview', views.index, name='preview'),
    path('preview/<int:behavior_model_id>', views.preview, name='preview'),
    path('brd/<int:behavior_model_id>', views.brd_download, name='get_brd'),
    path('result/<int:behavior_model_id>', views.result, name='get_result')
]
