"""
Module for managing built-in sample datasets for the Speech Emotion Recognition application.
This provides easy access to example audio files and their metadata.
"""

import os
import json
import logging
import random
from pathlib import Path
from django.conf import settings

logger = logging.getLogger(__name__)

# Path to the datasets directory
DATASETS_DIR = os.path.join(settings.BASE_DIR, 'datasets')

# Make sure the datasets directory exists
if not os.path.exists(DATASETS_DIR):
    try:
        os.makedirs(DATASETS_DIR)
        logger.info(f"Created datasets directory at {DATASETS_DIR}")
    except Exception as e:
        logger.error(f"Failed to create datasets directory: {str(e)}")

# Dataset metadata structure
DATASETS = {
    'ravdess': {
        'name': 'RAVDESS Dataset Samples',
        'description': 'The Ryerson Audio-Visual Database of Emotional Speech and Song (RAVDESS) contains 24 professional actors (12 female, 12 male), vocalizing two lexically-matched statements in a neutral North American accent.',
        'license': 'Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License.',
        'url': 'https://zenodo.org/record/1188976',
        'emotions': ['neutral', 'calm', 'happy', 'sad', 'angry', 'fearful', 'disgust', 'surprised'],
        'sample_directory': 'ravdess',
    },
    'tess': {
        'name': 'TESS Dataset Samples',
        'description': 'The Toronto Emotional Speech Set (TESS) dataset features a set of 200 target words spoken in the carrier phrase "Say the word _____" by two actresses (aged 26 and 64 years) in seven different emotions.',
        'license': 'Free for research use',
        'url': 'https://tspace.library.utoronto.ca/handle/1807/24487',
        'emotions': ['neutral', 'happy', 'sad', 'angry', 'fear', 'disgust', 'surprised'],
        'sample_directory': 'tess',
    },
    'savee': {
        'name': 'SAVEE Dataset Samples',
        'description': 'The Surrey Audio-Visual Expressed Emotion (SAVEE) database was recorded from four native English male speakers. The database consists of recordings of 120 utterances per speaker.',
        'license': 'Free for research use',
        'url': 'http://kahlan.eps.surrey.ac.uk/savee/',
        'emotions': ['neutral', 'happy', 'sad', 'angry', 'fear', 'disgust', 'surprised'],
        'sample_directory': 'savee',
    },
    'emovo': {
        'name': 'EMOVO Dataset Samples',
        'description': 'EMOVO is an Italian emotional speech dataset. It consists of recordings from 6 actors (3 male and 3 female), expressing 7 different emotional states.',
        'license': 'Free for research use',
        'url': 'http://voice.fub.it/activities/corpora/emovo/index.html',
        'emotions': ['neutral', 'happy', 'sad', 'angry', 'fear', 'disgust', 'surprised'],
        'sample_directory': 'emovo',
    }
}

def get_dataset_list():
    """
    Get a list of available datasets.
    Returns:
        List of dataset information dictionaries
    """
    result = []
    for dataset_id, dataset_info in DATASETS.items():
        # Recursively count .wav files in all subdirectories
        sample_dir = os.path.join(DATASETS_DIR, dataset_info['sample_directory'])
        sample_count = 0
        if os.path.exists(sample_dir):
            for root, dirs, files in os.walk(sample_dir):
                sample_count += len([f for f in files if f.endswith('.wav')])
        result.append({
            'id': dataset_id,
            'name': dataset_info['name'],
            'description': dataset_info['description'],
            'sample_count': sample_count,
            'emotions': dataset_info['emotions'],
        })
    return result

def get_dataset_samples(dataset_id, emotion=None, limit=10):
    """
    Get samples from a specific dataset, optionally filtered by emotion.
    Recursively searches for .wav files in all subdirectories.
    
    Args:
        dataset_id: ID of the dataset
        emotion: Optional emotion to filter samples by
        limit: Maximum number of samples to return
        
    Returns:
        List of file paths to audio samples
    """
    if dataset_id not in DATASETS:
        logger.error(f"Dataset {dataset_id} not found")
        return []
    
    dataset_info = DATASETS[dataset_id]
    sample_dir = os.path.join(DATASETS_DIR, dataset_info['sample_directory'])
    
    if not os.path.exists(sample_dir):
        logger.error(f"Sample directory {sample_dir} not found")
        return []
    
    # Recursively get all WAV files in the directory and subdirectories
    samples = []
    for root, dirs, files in os.walk(sample_dir):
        for f in files:
            if f.endswith('.wav'):
                samples.append(os.path.join(root, f))
    
    # Filter by emotion if specified
    if emotion:
        # Dataset-specific emotion filtering logic
        if dataset_id == 'ravdess':
            # RAVDESS naming format: .../03-01-01-01-01-01-01.wav
            emotion_codes = {
                'neutral': '01', 'calm': '02', 'happy': '03', 'sad': '04', 
                'angry': '05', 'fearful': '06', 'fear': '06', 'disgust': '07', 'surprised': '08'
            }
            if emotion in emotion_codes:
                code = emotion_codes[emotion]
                samples = [s for s in samples if os.path.basename(s).split('-')[2] == code]
        elif dataset_id == 'tess':
            # TESS naming format: .../OAF_back_happy.wav
            samples = [s for s in samples if f"_{emotion}." in os.path.basename(s).lower()]
        elif dataset_id == 'savee':
            # SAVEE naming format: .../DC_a01.wav
            emotion_codes = {
                'angry': 'a', 'anger': 'a', 'disgust': 'd', 'fear': 'f', 'fearful': 'f',
                'happy': 'h', 'happiness': 'h', 'neutral': 'n', 'sad': 'sa', 'sadness': 'sa',
                'surprised': 'su', 'surprise': 'su'
            }
            if emotion in emotion_codes:
                code = emotion_codes[emotion]
                samples = [s for s in samples if os.path.basename(s).split('_')[1].startswith(code)]
        elif dataset_id == 'emovo':
            # EMOVO naming format: .../m1-gio-1.wav
            emotion_codes = {
                'neutral': 'neu', 'happy': 'gio', 'sad': 'tri', 'angry': 'rab', 
                'fear': 'pau', 'fearful': 'pau', 'disgust': 'dis', 'surprised': 'sor'
            }
            if emotion in emotion_codes:
                code = emotion_codes[emotion]
                samples = [s for s in samples if os.path.basename(s).split('-')[1] == code]
    
    # Limit the number of samples
    if len(samples) > limit:
        samples = random.sample(samples, limit)
    
    return samples

def get_sample_metadata(file_path):
    """
    Extract metadata from a sample file path.
    
    Args:
        file_path: Path to the audio sample file
        
    Returns:
        Dictionary with metadata about the sample
    """
    file_name = os.path.basename(file_path)
    dataset_id = None
    emotion = None
    gender = None
    
    # Determine which dataset this file belongs to
    for d_id, d_info in DATASETS.items():
        if os.path.join(DATASETS_DIR, d_info['sample_directory']) in file_path:
            dataset_id = d_id
            break
    
    if dataset_id == 'ravdess':
        # Parse RAVDESS filename
        parts = file_name.split('-')
        if len(parts) >= 7:
            emotion_code = parts[2]
            intensity = parts[3]
            gender_code = 'male' if int(parts[6].split('.')[0]) % 2 == 1 else 'female'
            
            emotion_map = {
                '01': 'neutral', '02': 'calm', '03': 'happy', '04': 'sad',
                '05': 'angry', '06': 'fearful', '07': 'disgust', '08': 'surprised'
            }
            
            emotion = emotion_map.get(emotion_code, 'unknown')
            gender = gender_code
            
    elif dataset_id == 'tess':
        # Parse TESS filename
        parts = file_name.split('_')
        if len(parts) >= 3:
            age_gender = parts[0]
            emotion = parts[2].split('.')[0].lower()
            gender = 'female'  # TESS only has female speakers
            
    elif dataset_id == 'savee':
        # Parse SAVEE filename
        parts = file_name.split('_')
        if len(parts) >= 2:
            emotion_code = parts[1][:1] if not parts[1].startswith('s') else parts[1][:2]
            
            emotion_map = {
                'a': 'angry', 'd': 'disgust', 'f': 'fear',
                'h': 'happy', 'n': 'neutral', 'sa': 'sad', 'su': 'surprised'
            }
            
            emotion = emotion_map.get(emotion_code, 'unknown')
            gender = 'male'  # SAVEE only has male speakers
            
    elif dataset_id == 'emovo':
        # Parse EMOVO filename
        parts = file_name.split('-')
        if len(parts) >= 3:
            gender_code = parts[0][0]  # First character of actor code indicates gender
            emotion_code = parts[1]
            
            emotion_map = {
                'neu': 'neutral', 'gio': 'happy', 'tri': 'sad', 'rab': 'angry',
                'pau': 'fear', 'dis': 'disgust', 'sor': 'surprised'
            }
            
            emotion = emotion_map.get(emotion_code, 'unknown')
            gender = 'male' if gender_code.lower() == 'm' else 'female'
    
    return {
        'file_name': file_name,
        'file_path': file_path,
        'dataset': dataset_id,
        'emotion': emotion,
        'gender': gender,
    }

def count_samples_by_emotion():
    """
    Count the number of samples available for each emotion across all datasets.
    
    Returns:
        Dictionary with emotion counts
    """
    emotion_counts = {}
    
    for dataset_id, dataset_info in DATASETS.items():
        sample_dir = os.path.join(DATASETS_DIR, dataset_info['sample_directory'])
        
        if not os.path.exists(sample_dir):
            continue
            
        for emotion in dataset_info['emotions']:
            samples = get_dataset_samples(dataset_id, emotion, limit=1000)  # High limit to get all
            if emotion not in emotion_counts:
                emotion_counts[emotion] = 0
            emotion_counts[emotion] += len(samples)
    
    return emotion_counts

def create_sample_dataset_directory(dataset_id):
    """
    Create a directory for a dataset if it doesn't exist.
    
    Args:
        dataset_id: ID of the dataset
        
    Returns:
        Path to the created directory
    """
    if dataset_id not in DATASETS:
        logger.error(f"Dataset {dataset_id} not found")
        return None
    
    dataset_info = DATASETS[dataset_id]
    sample_dir = os.path.join(DATASETS_DIR, dataset_info['sample_directory'])
    
    if not os.path.exists(sample_dir):
        try:
            os.makedirs(sample_dir)
            logger.info(f"Created sample directory for {dataset_id} at {sample_dir}")
        except Exception as e:
            logger.error(f"Failed to create sample directory for {dataset_id}: {str(e)}")
            return None
    
    return sample_dir