from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import UserProfile, User


class SignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email']


class ChangeFieldsForm(forms.Form):
    new_email = forms.EmailField(max_length=100)
    new_avatar = forms.ImageField(required=False)

    def clean_new_avatar(self):
        new_avatar = self.cleaned_data.get('new_avatar')
        if new_avatar is not None and'image' not in new_avatar.content_type:
            raise forms.ValidationError('Wrong format of picture')
        return new_avatar

    def save(self):
        return self.cleaned_data


class UserProfileSignupForm(forms.ModelForm):

    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')
        if avatar is not None and'image' not in avatar.content_type:
            raise forms.ValidationError('Wrong format of picture')
        return avatar

    class Meta:
        model = UserProfile
        fields = ['avatar']
