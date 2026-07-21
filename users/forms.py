from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Profile, Snap

#  ФОРМА РЕЄСТРАЦІЇ КОРИСТУВАЧА
class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        # Поля, які користувач заповнює при реєстрації
        fields = ('username', 'email', 'birth_date', 'bio')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields['username'].label = "Ім'я користувача (Нікнейм)"
        self.fields['email'].label = "Електронна пошта"
        self.fields['birth_date'].label = "Дата народження"
        self.fields['bio'].label = "Біографія (Про себе)"
        self.fields['password1'].label = "Пароль"
        self.fields['password2'].label = "Підтвердження пароля"
        
        input_classes = 'mt-1 p-2 w-full bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:border-yellow-400'
        
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': input_classes
            })
            
        # Налаштування висоти для Біографії та типу для Календаря
        self.fields['bio'].widget.attrs.update({'rows': '3'})
        self.fields['birth_date'].widget = forms.DateInput(attrs={
            'type': 'date', 
            'class': input_classes
        })


#  ФОРМА РЕДАГУВАННЯ ДАНИХ КОРИСТУВАЧА
class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'bio', 'birth_date']
        labels = {
            'first_name': "Ім'я",
            'last_name': "Прізвище",
            'bio': "Біографія",
            'birth_date': "Дата народження",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        input_classes = 'w-full bg-slate-800 text-white rounded-xl p-3 border border-slate-700 focus:outline-none focus:border-yellow-400'

        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': input_classes})

        self.fields['bio'].widget.attrs.update({'rows': '3', 'placeholder': 'Розкажи про себе...'})
        self.fields['birth_date'].widget = forms.DateInput(attrs={
            'type': 'date',
            'class': input_classes
        })


#  ФОРМА ОНОВЛЕННЯ АВАТАРКИ ПРОФІЛЮ
class ProfileUpdateForm(forms.ModelForm):
    avatar = forms.ImageField(
        widget=forms.FileInput(attrs={'class': 'hidden', 'id': 'avatar-input'}),
        required=False,
        label="Аватар"
    )

    class Meta:
        model = Profile
        fields = ['avatar']


#  ФОРМА ВІДПРАВКИ СНАПУ
class SendSnapForm(forms.ModelForm):
    class Meta:
        model = Snap
        fields = ['receiver', 'media_file', 'duration']

    def __init__(self, *args, **kwargs):
        # Отримуємо поточного юзера з аргументів для фільтрації списку друзів
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Фільтруємо поле receiver тільки підтвердженими друзями
        if user:
            self.fields['receiver'].queryset = user.get_friends()

        self.fields['receiver'].label = "Отримувач (Друг)"
        self.fields['media_file'].label = "Медіа-файл (Фото/Відео)"
        self.fields['duration'].label = "Таймер перегляду (1-10 сек)"

        input_classes = 'w-full bg-slate-800 text-white rounded-xl p-3 border border-slate-700 focus:outline-none focus:border-yellow-400'

        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': input_classes})

        self.fields['duration'].widget.attrs.update({
            'placeholder': 'Безлімітно (або вкажи від 1 до 10)',
            'min': '1',
            'max': '10'
        })