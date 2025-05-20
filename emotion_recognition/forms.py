from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordResetForm, SetPasswordForm
from django.contrib.auth.models import User
from .models import AudioRecord


class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, help_text='Required. Enter a valid email address.')
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2',)
    
    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)
        # Add Tailwind CSS classes to form fields
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white dark:border-gray-600'


class AudioUploadForm(forms.ModelForm):
    class Meta:
        model = AudioRecord
        fields = ('audio_file',)
        
    def __init__(self, *args, **kwargs):
        super(AudioUploadForm, self).__init__(*args, **kwargs)
        self.fields['audio_file'].widget.attrs.update({
            'class': 'hidden',
            'accept': 'audio/wav'
        })
        self.fields['audio_file'].required = False


class CustomPasswordResetForm(PasswordResetForm):
    def __init__(self, *args, **kwargs):
        super(CustomPasswordResetForm, self).__init__(*args, **kwargs)
        # Add Tailwind CSS classes to form fields
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white dark:border-gray-600'


class CustomSetPasswordForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super(CustomSetPasswordForm, self).__init__(*args, **kwargs)
        # Add Tailwind CSS classes to form fields
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white dark:border-gray-600'
