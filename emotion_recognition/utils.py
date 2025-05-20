import os
import uuid
import wave
import datetime
import base64
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.conf import settings
import logging

# Configure logging
logger = logging.getLogger(__name__)

def base64_to_wav(base64_data, user_id=None):
    """
    Convert base64 audio data to WAV file
    
    Args:
        base64_data: base64 encoded audio data
        user_id: optional user ID for file naming
        
    Returns:
        Path to saved WAV file
    """
    try:
        # Remove data URL prefix if present
        if ',' in base64_data:
            base64_data = base64_data.split(',')[1]
        
        # Decode base64 data
        audio_data = base64.b64decode(base64_data)
        
        # Generate unique filename
        if user_id:
            file_name = f"recording_{user_id}_{uuid.uuid4()}.wav"
        else:
            file_name = f"recording_{uuid.uuid4()}.wav"
        
        # Define storage path
        today = datetime.datetime.now().strftime('%Y/%m/%d')
        file_path = os.path.join('audio_uploads', today, file_name)
        
        # Save the file
        saved_path = default_storage.save(file_path, ContentFile(audio_data))
        full_path = os.path.join(settings.MEDIA_ROOT, saved_path)
        
        return full_path
    
    except Exception as e:
        logger.error(f"Error saving base64 audio: {str(e)}")
        raise

def get_wav_duration(file_path):
    """
    Get duration of WAV file in seconds
    
    Args:
        file_path: Path to WAV file
        
    Returns:
        Duration in seconds
    """
    try:
        with wave.open(file_path, 'r') as wav_file:
            frames = wav_file.getnframes()
            rate = wav_file.getframerate()
            duration = frames / float(rate)
        return duration
    
    except Exception as e:
        logger.error(f"Error getting WAV duration: {str(e)}")
        return 0

def format_confidence(confidence):
    """Format confidence score as percentage"""
    return f"{confidence * 100:.1f}%"

def get_emotion_color(emotion):
    """Get color for emotion visualization"""
    colors = {
        'happy': 'text-yellow-500',
        'sad': 'text-blue-500',
        'angry': 'text-red-500',
        'neutral': 'text-gray-500',
        'fear': 'text-purple-500',
        'disgust': 'text-green-500',
        'surprised': 'text-pink-500'
    }
    return colors.get(emotion, 'text-gray-500')

def get_emotion_bg_color(emotion):
    """Get background color for emotion visualization"""
    colors = {
        'happy': 'bg-yellow-100',
        'sad': 'bg-blue-100',
        'angry': 'bg-red-100',
        'neutral': 'bg-gray-100',
        'fear': 'bg-purple-100',
        'disgust': 'bg-green-100',
        'surprised': 'bg-pink-100'
    }
    return colors.get(emotion, 'bg-gray-100')
