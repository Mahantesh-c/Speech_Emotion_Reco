import os
import json
import uuid
import logging
from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.urls import reverse
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

from .forms import SignUpForm, AudioUploadForm
from .models import AudioRecord, EmotionResult
from .audio_processor import process_audio_file
from .ml_model import predict_emotion

logger = logging.getLogger(__name__)

def index(request):
    """Homepage view."""
    return render(request, 'emotion_recognition/index.html')

def signup(request):
    """User registration view."""
    if request.user.is_authenticated:
        return redirect('emotion_recognition:dashboard')
    
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            messages.success(request, "Account created successfully!")
            return redirect('emotion_recognition:dashboard')
    else:
        form = SignUpForm()
    
    return render(request, 'emotion_recognition/signup.html', {'form': form})

def login_view(request):
    """User login view."""
    if request.user.is_authenticated:
        return redirect('emotion_recognition:dashboard')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('emotion_recognition:dashboard')
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    
    return render(request, 'emotion_recognition/login.html', {'form': form})

def dashboard(request):
    """User dashboard showing past emotion analyses."""
    # Get the user's recent emotion results
    results = EmotionResult.objects.filter(
        audio_record__user=request.user
    ).order_by('-created_at')[:10]
    
    upload_form = AudioUploadForm()
    
    return render(request, 'emotion_recognition/dashboard.html', {
        'results': results,
        'upload_form': upload_form
    })

def record_audio(request):
    """Page for recording or uploading audio."""
    upload_form = AudioUploadForm()
    
    if request.method == 'POST':
        upload_form = AudioUploadForm(request.POST, request.FILES)
        if upload_form.is_valid() and 'audio_file' in request.FILES:
            # Process uploaded file
            audio_record = upload_form.save(commit=False)
            audio_record.user = request.user
            audio_record.source = 'upload'
            audio_record.save()
            
            # Process the audio and predict emotion
            try:
                features = process_audio_file(audio_record.file_path)
                emotion, confidence, all_predictions = predict_emotion(features)
                
                # Save the emotion result
                emotion_result = EmotionResult.objects.create(
                    audio_record=audio_record,
                    emotion=emotion,
                    confidence=confidence,
                    full_results=all_predictions
                )
                
                return redirect('emotion_recognition:result', result_id=emotion_result.id)
            
            except Exception as e:
                logger.error(f"Error processing audio: {str(e)}")
                messages.error(request, f"Error processing audio: {str(e)}")
                return redirect('emotion_recognition:record')
    
    return render(request, 'emotion_recognition/record_minimal.html', {
        'upload_form': upload_form
    })

def view_result(request, result_id):
    """View the result of emotion analysis."""
    result = get_object_or_404(EmotionResult, id=result_id, audio_record__user=request.user)
    return render(request, 'emotion_recognition/result.html', {'result': result})

def profile(request):
    """User profile page."""
    # Get all emotion results for the user
    results = EmotionResult.objects.filter(
        audio_record__user=request.user
    ).order_by('-created_at')
    
    # Calculate statistics
    emotion_counts = {}
    for result in results:
        emotion = result.emotion
        if emotion in emotion_counts:
            emotion_counts[emotion] += 1
        else:
            emotion_counts[emotion] = 1
    
    return render(request, 'emotion_recognition/profile.html', {
        'results': results,
        'emotion_counts': emotion_counts
    })

@require_POST
@csrf_exempt
def process_audio(request):
    """API endpoint to process uploaded audio files."""
    if request.FILES.get('audio_file'):
        try:
            file = request.FILES['audio_file']
            
            # Save the uploaded file
            file_name = f"recording_{uuid.uuid4()}.wav"
            file_path = os.path.join('audio_uploads', datetime.now().strftime('%Y/%m/%d'), file_name)
            saved_path = default_storage.save(file_path, file)
            full_path = os.path.join(settings.MEDIA_ROOT, saved_path)
            
            # Create audio record in database
            audio_record = AudioRecord.objects.create(
                user=request.user,
                file_path=full_path,
                source='upload'
            )
            
            # Process the audio file with enhanced error handling
            try:
                logger.info(f"Starting audio analysis for file: {full_path}")
                features = process_audio_file(full_path)
                emotion, confidence, all_predictions = predict_emotion(features)
                logger.info(f"Audio analysis complete. Detected emotion: {emotion}, confidence: {confidence:.2f}")
            except Exception as e:
                logger.error(f"Error during audio analysis: {str(e)}")
                logger.exception("Stack trace:")
                return JsonResponse({
                    'success': False,
                    'error': f"An error occurred during analysis: {str(e)}"
                }, status=400)
            
            # Save the emotion result
            emotion_result = EmotionResult.objects.create(
                audio_record=audio_record,
                emotion=emotion,
                confidence=confidence,
                full_results=all_predictions
            )
            
            # Return the result
            return JsonResponse({
                'success': True,
                'result_id': emotion_result.id,
                'emotion': emotion,
                'confidence': confidence,
                'result_url': reverse('emotion_recognition:result', args=[emotion_result.id])
            })
            
        except Exception as e:
            logger.error(f"Error processing audio: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
    
    return JsonResponse({'success': False, 'error': 'No audio file provided'}, status=400)

@require_POST
@csrf_exempt
def save_recording(request):
    """API endpoint to save recorded audio from browser."""
    if request.body:
        try:
            # Get the raw audio data
            audio_data = request.body
            
            # Save the recording
            file_name = f"recording_{uuid.uuid4()}.wav"
            file_path = os.path.join('audio_uploads', datetime.now().strftime('%Y/%m/%d'), file_name)
            saved_path = default_storage.save(file_path, ContentFile(audio_data))
            full_path = os.path.join(settings.MEDIA_ROOT, saved_path)
            
            # Create audio record in database
            audio_record = AudioRecord.objects.create(
                user=request.user,
                file_path=full_path,
                source='record'
            )
            
            # Process the audio file with enhanced error handling
            try:
                logger.info(f"Starting audio analysis for recording: {full_path}")
                features = process_audio_file(full_path)
                emotion, confidence, all_predictions = predict_emotion(features)
                logger.info(f"Audio analysis complete. Detected emotion: {emotion}, confidence: {confidence:.2f}")
            except Exception as e:
                logger.error(f"Error during audio analysis: {str(e)}")
                logger.exception("Stack trace:")
                return JsonResponse({
                    'success': False,
                    'error': f"An error occurred during analysis: {str(e)}"
                }, status=400)
            
            # Save the emotion result
            emotion_result = EmotionResult.objects.create(
                audio_record=audio_record,
                emotion=emotion,
                confidence=confidence,
                full_results=all_predictions
            )
            
            # Return the result
            return JsonResponse({
                'success': True,
                'result_id': emotion_result.id,
                'emotion': emotion,
                'confidence': confidence,
                'result_url': reverse('emotion_recognition:result', args=[emotion_result.id])
            })
            
        except Exception as e:
            logger.error(f"Error saving recording: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
    
    return JsonResponse({'success': False, 'error': 'No audio data provided'}, status=400)