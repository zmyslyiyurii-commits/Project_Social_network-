from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

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