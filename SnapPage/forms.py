from django import forms
from users.models import Story, Snap, User


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


class SnapForm(forms.ModelForm):
    class Meta:
        model = Snap
        fields = ['receiver', 'media_file', 'duration']
        widgets = {
            'receiver': forms.Select(attrs={
                'class': 'w-full bg-[#121212] border border-[#3d3d3d] focus:border-[#fffc00] text-white rounded-xl p-3 outline-none transition text-sm'
            }),
            'media_file': forms.FileInput(attrs={
                'class': 'hidden',
                'id': 'id_snap_media_file',
                'accept': 'image/*,video/*'
            }),
            'duration': forms.NumberInput(attrs={
                'class': 'w-full bg-[#121212] border border-[#3d3d3d] focus:border-[#fffc00] text-white rounded-xl p-3 outline-none transition text-sm',
                'min': 1,
                'max': 10
            })
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user:
            # Виводимо строго лише підтверджених друзів користувача
            self.fields['receiver'].queryset = user.get_friends()
        else:
            self.fields['receiver'].queryset = User.objects.none()