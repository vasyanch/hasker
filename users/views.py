from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.views import View

from .forms import SignupForm, UserProfileSignupForm, ChangeFieldsForm
from qa.models import Question


class SignUpView(View):
    form = SignupForm
    profile_form = UserProfileSignupForm
    template_name = 'users/signup.html'

    def __init__(self, *args, **kwargs):
        super(SignUpView, self).__init__(*args, **kwargs)
        self.context = {'trending': Question.objects.popular()}

    def get(self, request, *args, **kwargs):
        self.context['form'] = self.form()
        self.context['profile_form'] = self.profile_form()
        return render(request, self.template_name, self.context)

    def post(self, request, *args, **kwargs):
        form = self.form(request.POST)
        profile_form = self.profile_form(request.POST, request.FILES)
        if form.is_valid() and profile_form.is_valid():
            new_user = form.save()
            ava_form = profile_form.save(commit=False)
            new_user.userprofile.avatar = ava_form.avatar
            new_user.save()
            username = new_user.get_username()
            password = request.POST.get('password1')
            user = authenticate(request, username=username, password=password)
            login(request, user)
            url = request.POST.get('continue', '/')
            return HttpResponseRedirect(url)
        self.context['form'] = form
        self.context['profile_form'] = profile_form
        return render(request, self.template_name, self.context)


class LogInView(View):
    form = AuthenticationForm
    template_name = 'users/login.html'

    def __init__(self, *args, **kwargs):
        super(LogInView, self).__init__(*args, **kwargs)
        self.context = {
            'trending': Question.objects.popular(),
            'error': ''
        }

    def get(self, request, *args, **kwargs):
        form = self.form()
        self.context['form'] = form
        return render(request, self.template_name, self.context)

    def post(self, request, *args, **kwargs):
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            url = request.POST.get('continue', '/')
            return HttpResponseRedirect(url)
        self.context['form'] = self.form()
        self.context['error'] = 'Invalid username/password'
        return render(request, self.template_name, self.context)


class ProfileView(View):
    template_name = 'users/profile.html'

    def __init__(self, *args, **kwargs):
        super(ProfileView, self).__init__(*args, **kwargs)
        self.context = {
            'trending': Question.objects.popular(),
            'error': ''
        }

    def get(self, request, *args, **kwargs):
        self.context['user'] = request.user
        if request.user.id != self.kwargs['id_user']:
            self.context['error'] = 'Sorry!\nYou can watch only your profile page'
        else:
            self.context['error'] = ''
        return render(request, self.template_name, self.context)

    def post(self, request, *args, **kwargs):
        user = request.user
        change = request.POST.get('change_choice')
        if change == "Change question":
            user.userprofile.cancel_vote_question()
        if change == "Change answer":
            user.userprofile.cancel_vote_answer()
        user.userprofile.save()
        self.context['user'] = user
        return render(request, self.template_name, self.context)


class EditProfileView(View):
    new_fields_form = ChangeFieldsForm
    template_name = 'users/edit_profile.html'

    def __init__(self, *args, **kwargs):
        super(EditProfileView, self).__init__(*args, **kwargs)
        self.context = {'trending': Question.objects.popular()}

    def get(self, request, *args, **kwargs):
        self.context['new_fields_form'] = self.new_fields_form(initial={'new_email': request.user.email})
        return render(request, self.template_name, self.context)

    def post(self, request, *args, **kwargs):
        new_fields_form = self.new_fields_form(request.POST, request.FILES)
        if new_fields_form.is_valid():
            user = request.user
            new_fields = new_fields_form.save()
            user.email = new_fields['new_email']
            if request.FILES:
                user.userprofile.avatar = new_fields['new_avatar']
            user.save()
            url = user.userprofile.get_url()
            return HttpResponseRedirect(url)
        self.context['new_fields_form'] = new_fields_form
        return render(request, self.template_name, self.context)


def logout_view(request):
    logout(request)
    return redirect(request.GET.get('continue', '/'))
