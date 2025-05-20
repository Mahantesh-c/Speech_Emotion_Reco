"""
Views for handling sample datasets in the Speech Emotion Recognition application.
"""

import os
import json
import logging
import tempfile
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET
from django.conf import settings
from django.core.paginator import Paginator
from django.db import transaction

from .models import SampleDataset, AudioRecord, EmotionResult
from .datasets import (
    get_dataset_list, get_dataset_samples, get_sample_metadata,
    count_samples_by_emotion, DATASETS, DATASETS_DIR
)
from .audio_processor import process_audio_file
from .ml_model import predict_emotion

logger = logging.getLogger(__name__)

@login_required
def sample_datasets(request):
    """View to list all available sample datasets."""
    # Get dataset information from the datasets module
    datasets_info = get_dataset_list()
    
    # Map to SampleDataset model objects (create if they don't exist)
    datasets = []
    for info in datasets_info:
        dataset, created = SampleDataset.objects.get_or_create(
            dataset_id=info['id'],
            defaults={
                'name': info['name'],
                'description': info['description'],
                'sample_count': info['sample_count'],
                'metadata': {'emotions': info['emotions']}
            }
        )
        
        # Update fields if the dataset already exists
        if not created and dataset.sample_count != info['sample_count']:
            dataset.sample_count = info['sample_count']
            dataset.save()
        
        # Get dataset info from the DATASETS dictionary for additional fields
        dataset_extra_info = DATASETS.get(info['id'], {})
        dataset.source_url = dataset_extra_info.get('url')
        dataset.license = dataset_extra_info.get('license')
        dataset.emotions = info['emotions']
        
        datasets.append(dataset)
    
    return render(request, 'emotion_recognition/sample_datasets.html', {
        'datasets': datasets
    })

@login_required
def dataset_detail(request, dataset_id):
    """View to display details of a specific dataset and its samples."""
    # Get the dataset
    dataset = get_object_or_404(SampleDataset, id=dataset_id)
    
    # Get additional information from the DATASETS dictionary
    dataset_info = DATASETS.get(dataset.dataset_id, {})
    dataset.emotions = dataset.metadata.get('emotions', [])
    dataset.source_url = dataset_info.get('url')
    dataset.license = dataset_info.get('license')
    
    # Get filter parameters
    selected_emotion = request.GET.get('emotion')
    
    # Get samples for this dataset
    samples = get_dataset_samples(dataset.dataset_id, emotion=selected_emotion, limit=100)
    
    # Process each sample to get its metadata
    sample_data = []
    for sample_path in samples:
        metadata = get_sample_metadata(sample_path)
        sample_data.append(metadata)
    
    # Paginate results
    paginator = Paginator(sample_data, 12)  # 12 samples per page
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'emotion_recognition/dataset_detail.html', {
        'dataset': dataset,
        'samples': page_obj,
        'selected_emotion': selected_emotion,
        'is_paginated': paginator.num_pages > 1,
        'page_obj': page_obj
    })

@login_required
def analyze_dataset(request, dataset_id):
    """View to run analysis on a dataset or display analysis results."""
    # Get the dataset
    dataset = get_object_or_404(SampleDataset, id=dataset_id)
    
    # Get additional information from the DATASETS dictionary
    dataset_info = DATASETS.get(dataset.dataset_id, {})
    dataset.emotions = dataset.metadata.get('emotions', [])
    dataset.source_url = dataset_info.get('url')
    dataset.license = dataset_info.get('license')
    
    # Check if we should start a new analysis
    start_analysis = request.GET.get('start', '0') == '1'
    
    # Get emotion distribution
    emotion_distribution = count_samples_by_emotion()
    filtered_distribution = {k: v for k, v in emotion_distribution.items() if k in dataset.emotions}
    
    # Check analysis status
    # In a real application, this would be stored in the database or a task queue
    # For simplicity, we're using a flag in the metadata
    analysis_metadata = dataset.metadata.get('analysis', {})
    analysis_status = analysis_metadata.get('status', 'not_started')
    
    # If starting a new analysis, update the status and metadata
    if start_analysis and analysis_status != 'running':
        analysis_status = 'running'
        analysis_metadata['status'] = 'running'
        analysis_metadata['progress'] = 0
        analysis_metadata['completed_count'] = 0
        analysis_metadata['total_count'] = dataset.sample_count
        dataset.metadata['analysis'] = analysis_metadata
        dataset.save()
        
        # In a real application, you would start a background task here
        # For now, we'll run a simple analysis directly in the view
        if dataset.sample_count > 0:
            analyze_dataset_samples(dataset)
    
    # Get analysis results if available
    if analysis_status == 'complete':
        analysis_results = analysis_metadata.get('results', {})
        overall_accuracy = analysis_results.get('overall_accuracy', 0)
        accuracy_by_emotion = analysis_results.get('accuracy_by_emotion', {})
        confusion_matrix = analysis_results.get('confusion_matrix', {})
        sample_results = analysis_results.get('sample_results', [])
    else:
        # Default values if analysis is not complete
        overall_accuracy = 0
        accuracy_by_emotion = {}
        confusion_matrix = {'emotions': [], 'matrix': []}
        sample_results = []
    
    # Update progress information
    progress = 0
    completed_count = 0
    total_count = dataset.sample_count
    
    if analysis_status == 'running':
        progress = analysis_metadata.get('progress', 0)
        completed_count = analysis_metadata.get('completed_count', 0)
        total_count = analysis_metadata.get('total_count', dataset.sample_count)
    
    return render(request, 'emotion_recognition/dataset_analysis.html', {
        'dataset': dataset,
        'analysis_status': analysis_status,
        'emotion_distribution': filtered_distribution,
        'overall_accuracy': overall_accuracy,
        'accuracy_by_emotion': accuracy_by_emotion,
        'confusion_matrix': confusion_matrix,
        'sample_results': sample_results,
        'progress': progress,
        'completed_count': completed_count,
        'total_count': total_count
    })

@login_required
@require_GET
def sample_audio(request, dataset_id, file_name):
    """View to serve audio files from sample datasets."""
    # Get the dataset
    dataset = get_object_or_404(SampleDataset, id=dataset_id)
    
    # Get all samples for this dataset
    samples = get_dataset_samples(dataset.dataset_id, limit=1000)
    
    # Find the requested sample
    sample_path = None
    for path in samples:
        if os.path.basename(path) == file_name:
            sample_path = path
            break
    
    if not sample_path or not os.path.exists(sample_path):
        return HttpResponse(status=404)
    
    # Serve the audio file
    with open(sample_path, 'rb') as f:
        response = HttpResponse(f.read(), content_type='audio/wav')
        response['Content-Disposition'] = f'inline; filename="{file_name}"'
        return response

@login_required
@require_GET
def analyze_sample(request):
    """API endpoint to analyze a specific sample audio file."""
    sample_path = request.GET.get('path')

    # Security: Only allow files inside the datasets directory
    if not sample_path or not os.path.exists(sample_path) or not os.path.abspath(sample_path).startswith(os.path.abspath(DATASETS_DIR)):
        return JsonResponse({'success': False, 'error': 'Sample not found or not allowed'}, status=404)

    try:
        # Process the audio file
        features = process_audio_file(sample_path)
        emotion, confidence, all_predictions = predict_emotion(features)

        # Return the result
        return JsonResponse({
            'success': True,
            'emotion': emotion,
            'confidence': confidence,
            'full_results': all_predictions
        })
    except Exception as e:
        logger.error(f"Error analyzing sample {sample_path}: {str(e)}")
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

def analyze_dataset_samples(dataset):
    """
    Run analysis on all samples in a dataset.
    
    Args:
        dataset: The SampleDataset model object
    """
    # Get all samples for this dataset
    all_samples = get_dataset_samples(dataset.dataset_id, limit=1000)
    
    # Initialize counters and results
    total_count = len(all_samples)
    completed_count = 0
    correct_count = 0
    
    # Initialize confusion matrix
    emotions = dataset.metadata.get('emotions', [])
    confusion_matrix = {
        'emotions': emotions,
        'matrix': [[0 for _ in range(len(emotions))] for _ in range(len(emotions))]
    }
    
    # Initialize accuracy by emotion
    emotion_correct = {emotion: 0 for emotion in emotions}
    emotion_total = {emotion: 0 for emotion in emotions}
    
    # Sample results
    sample_results = []
    
    # Process each sample
    for i, sample_path in enumerate(all_samples):
        try:
            # Get sample metadata
            metadata = get_sample_metadata(sample_path)
            true_emotion = metadata.get('emotion')
            
            # Skip if no true emotion
            if not true_emotion or true_emotion not in emotions:
                continue
            
            # Process the audio file
            features = process_audio_file(sample_path)
            predicted_emotion, confidence, all_predictions = predict_emotion(features)
            
            # Update counters
            emotion_total[true_emotion] = emotion_total.get(true_emotion, 0) + 1
            
            # Check if prediction is correct
            is_correct = predicted_emotion == true_emotion
            if is_correct:
                correct_count += 1
                emotion_correct[true_emotion] = emotion_correct.get(true_emotion, 0) + 1
            
            # Update confusion matrix
            true_idx = emotions.index(true_emotion)
            pred_idx = emotions.index(predicted_emotion) if predicted_emotion in emotions else -1
            
            if pred_idx >= 0:
                confusion_matrix['matrix'][true_idx][pred_idx] += 1
            
            # Add to sample results
            sample_results.append({
                'sample_name': os.path.basename(sample_path),
                'true_emotion': true_emotion,
                'predicted_emotion': predicted_emotion,
                'confidence': confidence,
                'confidence_percent': int(confidence * 100),
                'is_correct': is_correct
            })
            
            # Update progress
            completed_count += 1
            progress = int((completed_count / total_count) * 100) if total_count > 0 else 0
            
            # Update dataset metadata
            with transaction.atomic():
                # Reload dataset to avoid race conditions
                current_dataset = SampleDataset.objects.get(id=dataset.id)
                current_metadata = current_dataset.metadata
                current_metadata.setdefault('analysis', {})
                current_metadata['analysis']['progress'] = progress
                current_metadata['analysis']['completed_count'] = completed_count
                current_metadata['analysis']['total_count'] = total_count
                current_dataset.metadata = current_metadata
                current_dataset.save()
            
        except Exception as e:
            logger.error(f"Error analyzing sample {sample_path}: {str(e)}")
            # Continue with next sample
    
    # Calculate overall accuracy
    overall_accuracy = int((correct_count / completed_count) * 100) if completed_count > 0 else 0
    
    # Calculate accuracy by emotion
    accuracy_by_emotion = {}
    for emotion in emotions:
        if emotion_total.get(emotion, 0) > 0:
            accuracy_by_emotion[emotion] = int((emotion_correct.get(emotion, 0) / emotion_total.get(emotion, 1)) * 100)
        else:
            accuracy_by_emotion[emotion] = 0
    
    # Prepare results
    analysis_results = {
        'overall_accuracy': overall_accuracy,
        'accuracy_by_emotion': accuracy_by_emotion,
        'confusion_matrix': confusion_matrix,
        'sample_results': sample_results
    }
    
    # Update dataset metadata with results
    with transaction.atomic():
        # Reload dataset to avoid race conditions
        final_dataset = SampleDataset.objects.get(id=dataset.id)
        final_metadata = final_dataset.metadata
        final_metadata.setdefault('analysis', {})
        final_metadata['analysis']['status'] = 'complete'
        final_metadata['analysis']['progress'] = 100
        final_metadata['analysis']['completed_count'] = completed_count
        final_metadata['analysis']['total_count'] = total_count
        final_metadata['analysis']['results'] = analysis_results
        final_dataset.metadata = final_metadata
        final_dataset.save()
    
    return analysis_results