from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'video_handler'

urlpatterns = [
    path('', views.index, name='index'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('upload/', views.upload_video, name='upload_video'),
    path('my-videos/', views.my_videos, name='my_videos'),
    path('video/<int:video_id>/', views.video_detail, name='video_detail'),
    path('step/<int:step_id>/edit/', views.edit_step, name='edit_step'),
    path('step/<int:step_id>/delete/', views.delete_step, name='delete_step'),
    path('step/<int:step_id>/move/<str:direction>/', views.reorder_step, name='reorder_step'),
    path('video/<int:video_id>/bpmn/', views.bpmn_viewer, name='bpmn_viewer'),
    path('video/<int:video_id>/bpmn/save/', views.save_bpmn, name='save_bpmn'),
    path('video/<int:video_id>/bpmn/load/', views.load_bpmn, name='load_bpmn'),
    path('video/<int:video_id>/bpmn/update-steps/', views.update_steps_from_bpmn, name='update_steps_from_bpmn'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 