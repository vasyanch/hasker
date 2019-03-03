from django import forms
from django.contrib.auth.forms import UserCreationForm, User

from .models import UserProfile, User


class SignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email']


class UserProfileSignupForm(forms.ModelForm):

    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')
        if avatar is not None and'image' not in avatar.content_type:
            raise forms.ValidationError('Wrong format of picture')
        return avatar

    class Meta:
        model = UserProfile
        fields = ['avatar']
