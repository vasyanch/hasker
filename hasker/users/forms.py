from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import UserProfile, User


class SignupForm(UserCreationForm):

    username = forms.CharField(widget=forms.TextInput(), max_length=30, label='Login')
    email = forms.EmailField(widget=forms.TextInput(), required=True, max_length=100, label='Email')
    password1 = forms.CharField(widget=forms.PasswordInput(), min_length=6, label='Password')
    password2 = forms.CharField(widget=forms.PasswordInput(), min_length=6, label='Repeat password')

    class Meta:
        model = User
        fields = ['username', 'email']


class UserProfileSignupForm(forms.ModelForm):
    avatar = forms.ImageField(widget=forms.ClearableFileInput(), required=False, label='Avatar')

    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')
        #if avatar is None:
        #    raise forms.ValidationError('Add picture,')
        if avatar is not None and'image' not in avatar.content_type:
            raise forms.ValidationError('Wrong format of picture')
        return avatar

    class Meta:
        model = UserProfile
        fields = ['avatar']
