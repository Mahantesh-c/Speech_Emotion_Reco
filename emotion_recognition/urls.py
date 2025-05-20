from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from . import views
from . import dataset_views
from .forms import CustomPasswordResetForm, CustomSetPasswordForm

app_name = 'emotion_recognition'

urlpatterns = [
    # Public pages
    path('', views.index, name='index'),
    
    # Authentication
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('signup/', views.signup, name='signup'),
    
    # Password reset
    path('password_reset/', auth_views.PasswordResetView.as_view(
        template_name='emotion_recognition/password_reset.html',
        form_class=CustomPasswordResetForm,
        email_template_name='emotion_recognition/password_reset_email.html',
        success_url='/password_reset/done/'
    ), name='password_reset'),
    
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='emotion_recognition/password_reset_done.html'
    ), name='password_reset_done'),
    
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='emotion_recognition/password_reset_confirm.html',
        form_class=CustomSetPasswordForm,
        success_url='/reset/done/'
    ), name='password_reset_confirm'),
    
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='emotion_recognition/password_reset_complete.html'
    ), name='password_reset_complete'),
    
    # Protected pages
    path('dashboard/', login_required(views.dashboard), name='dashboard'),
    path('record/', login_required(views.record_audio), name='record'),
    path('result/<int:result_id>/', login_required(views.view_result), name='result'),
    path('profile/', login_required(views.profile), name='profile'),
    
    
    path('datasets/', login_required(dataset_views.sample_datasets), name='sample_datasets'),
    path('datasets/<int:dataset_id>/', login_required(dataset_views.dataset_detail), name='dataset_detail'),
    path('datasets/<int:dataset_id>/analyze/', login_required(dataset_views.analyze_dataset), name='analyze_dataset'),
    path('datasets/<int:dataset_id>/audio/<str:file_name>/', login_required(dataset_views.sample_audio), name='sample_audio'),
    # API endpoints
    path('api/process-audio/', login_required(views.process_audio), name='process_audio'),
    path('api/save-recording/', login_required(views.save_recording), name='save_recording'),
    path('api/analyze-sample/', login_required(dataset_views.analyze_sample), name='analyze_sample'),
]

