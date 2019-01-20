from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout

from .forms import SignupForm, UserProfileSignupForm
from .models import UserProfile, User
from qa.models import Question


def signup(request):
    trending = Question.objects.popular()
    form = SignupForm(request.POST or None)
    profile_form = UserProfileSignupForm(request.POST or None, request.FILES or None)
    if request.method == 'POST':
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
    return render(request, 'users/signup.html', {
        'form': form,
        'profile_form': profile_form,
        'trending': trending,
    })


def login_(request):
    error = ''
    form = SignupForm()
    trending = Question.objects.popular()
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password1')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            url = request.POST.get('continue', '/')
            return HttpResponseRedirect(url)
        else:
            error = 'Invalid username/password'
    return render(request,  'users/login.html', {
        'form': form,
        'error': error,
        'trending': trending,
    })


def logout_(request):
    logout(request)
    return HttpResponseRedirect(request.GET.get('continue', '/'))


def profile(request, id_user):
    error = ''
    user = request.user
    trending = Question.objects.popular()
    ref_to_avatar = user.userprofile.avatar.url.split('/')
    ref_to_avatar = '/'.join(ref_to_avatar[2:])
    if request.user.id != id_user:
        error = 'Sorry!\nYou can watch only your profile page'
    return render(request, 'users/profile.html',{
        'ref_to_avatar': ref_to_avatar,
        'user': user,
        'trending': trending,
        'error': error,
    })
