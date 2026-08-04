from django import forms
from users.models import Story

class StoryForm(forms.ModelForm):
    class Meta:
        model = Story
        fields = ['media_file']
        widgets = {
            'media_file': forms.FileInput(attrs={
                'class': 'hidden',
                'id': 'story-file-input',
                'accept': 'image/*,video/*'
            })
        }