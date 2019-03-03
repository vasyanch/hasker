from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.views import View


from .forms import SignupForm, UserProfileSignupForm
from qa.models import Question


class SignUpView(View):
    form = SignupForm
    profile_form = UserProfileSignupForm
    context = {'trending': Question.objects.popular()}
    template_name = 'users/signup.html'

    def get(self, request, *args, **kwargs):
        form = self.form()
        profile_form = self.profile_form()
        self.context['form'] = form
        self.context['profile_form'] = profile_form
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
        else:
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


def logout_view(request):
    logout(request)
    return redirect(request.GET.get('continue', '/'))
