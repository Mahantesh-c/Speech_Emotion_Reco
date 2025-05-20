from django.contrib import admin
from .models import AudioRecord, EmotionResult

@admin.register(AudioRecord)
class AudioRecordAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'file_path', 'source')
    list_filter = ('source', 'created_at')
    search_fields = ('user__username', 'file_path')
    date_hierarchy = 'created_at'

@admin.register(EmotionResult)
class EmotionResultAdmin(admin.ModelAdmin):
    list_display = ('audio_record', 'emotion', 'confidence', 'created_at')
    list_filter = ('emotion', 'created_at')
    search_fields = ('audio_record__user__username', 'emotion')
    date_hierarchy = 'created_at'
