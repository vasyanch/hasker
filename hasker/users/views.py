from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.views import View

from .forms import SignupForm, UserProfileSignupForm, ChangeEmailForm
from qa.models import Question


class SignUpView(View):
    form = SignupForm
    profile_form = UserProfileSignupForm
    context = {'trending': Question.objects.popular()}
    template_name = 'users/signup.html'

    def get(self, request, *args, **kwargs):
        self.context['form'] = self.form()
        self.context['profile_form'] = self.profile_form()
        return render(request, self.template_name, self.context)

    def post(self, request, *args, **kwargs):
        form = self.form(request.POST)
        profile_form = self.profile_form(request.POST, request.FILES)
        if form.is_valid() and profile_form.is_valid():
            new_user = form.save()
            user_profile = profile_form.save(commit=False)
            user_profile.user = new_user
            user_profile.save()
            username = new_user.username
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
    context = {
        'trending': Question.objects.popular(),
        'error': ''
    }
    template_name = 'users/login.html'

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
        self.context['error'] = 'Invalid username/password'
        return render(request, self.template_name, self.context)


class ProfileView(View):
    context = {
        'trending': Question.objects.popular(),
        'error': ''
    }
    template_name = 'users/profile.html'

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
    form_email = ChangeEmailForm
    form_avatar = UserProfileSignupForm
    context = {'trending': Question.objects.popular()}
    template_name = 'users/edit_profile.html'

    def get(self, request, *args, **kwargs):
        self.context['form_email'] = self.form_email(initial={'new_email': request.user.email})
        self.context['form_avatar'] = self.form_avatar(initial={'avatar': request.user.userprofile.avatar})
        return render(request, self.template_name, self.context)

    def post(self, request, *args, **kwargs):
        form_email = self.form_email(request.POST)
        form_avatar = self.form_avatar(request.POST, request.FILES)
        if form_email.is_valid() and form_avatar.is_valid():
            user = request.user
            new_email = form_email.save()
            user.email = new_email
            user.userprofile.avatar = form_avatar.clean_avatar()
            user.userprofile.save()
            user.save()
            url = user.userprofile.get_url()
            return HttpResponseRedirect(url)
        self.context['form_email'] = form_email
        self.context['form_avatar'] = form_avatar
        return render(request, self.template_name, self.context)


def logout_view(request):
    logout(request)
    return redirect(request.GET.get('continue', '/'))
