from django.db import models
from django.contrib.auth.models import User
import os


class AudioRecord(models.Model):
    SOURCE_CHOICES = (
        ('upload', 'Uploaded File'),
        ('record', 'Browser Recording'),
        ('sample', 'Sample Dataset'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='audio_records')
    audio_file = models.FileField(upload_to='audio_uploads/%Y/%m/%d/')
    file_path = models.CharField(max_length=255)
    source = models.CharField(max_length=10, choices=SOURCE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    emotion = models.CharField(max_length=100)
    
    # Sample dataset information
    dataset = models.CharField(max_length=50, null=True, blank=True)
    is_sample = models.BooleanField(default=False)
    sample_metadata = models.JSONField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.username}'s recording - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
    
    def save(self, *args, **kwargs):
        # Set file_path based on audio_file path if uploading a file
        if self.audio_file and not self.file_path:
            try:
                self.file_path = self.audio_file.path
            except ValueError:
                # Handle case where file is not set
                pass
        super(AudioRecord, self).save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        # Delete the actual file when model instance is deleted, but not sample datasets
        if not self.is_sample:
            try:
                if os.path.isfile(self.file_path):
                    try:
                        os.remove(self.file_path)
                    except Exception as e:
                        # Log error but continue with model deletion
                        import logging
                        logger = logging.getLogger(__name__)
                        logger.warning(f"Error deleting audio file: {e}")
            except Exception:
                # Handle any errors checking file existence
                pass
        
        super(AudioRecord, self).delete(*args, **kwargs)
        
    @property
    def audio_file_exists(self):
        """Check if the associated audio file exists"""
        # For sample datasets, check the file_path directly
        if self.is_sample:
            return os.path.isfile(self.file_path)
        
        # For user uploads, check the audio_file field
        try:
            return self.audio_file and os.path.exists(self.audio_file.path)
        except (ValueError, FileNotFoundError, AttributeError):
            return False


class EmotionResult(models.Model):
    EMOTION_CHOICES = (
        ('happy', 'Happy'),
        ('sad', 'Sad'),
        ('angry', 'Angry'),
        ('neutral', 'Neutral'),
        ('fear', 'Fear'),
        ('disgust', 'Disgust'),
        ('surprised', 'Surprised'),
    )
    
    audio_record = models.OneToOneField(AudioRecord, on_delete=models.CASCADE, related_name='emotion_result')
    emotion = models.CharField(max_length=20, choices=EMOTION_CHOICES)
    confidence = models.FloatField()
    full_results = models.JSONField(null=True, blank=True)  # Store detailed prediction results if needed
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Emotion: {self.emotion} ({self.confidence:.2f})"


class SampleDataset(models.Model):
    """Model for tracking sample datasets"""
    dataset_id = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    sample_count = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    
    source_url = models.URLField(blank=True, null=True)
    license = models.CharField(max_length=255, blank=True, null=True)
    metadata = models.JSONField(null=True, blank=True)
    def __str__(self):
        return f"{self.name} ({self.sample_count} samples)"
    
    class Meta:
        verbose_name = "Sample Dataset"
        verbose_name_plural = "Sample Datasets"
