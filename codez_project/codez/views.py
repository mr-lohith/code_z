from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q

from .forms import LoginForm, RegisterForm
from .models import Problem, UserProfile


# ─── Auth Views ──────────────────────────────────────────────────────────────

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    form = LoginForm(request, data=request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            next_url = request.GET.get('next', 'home')
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'codez/login.html', {'form': form})


def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    form = RegisterForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            user = form.save()
            # Auto-create profile
            UserProfile.objects.get_or_create(user=user)
            login(request, user)
            messages.success(request, f'Account created! Welcome to CodeZ, {user.username}!')
            return redirect('home')
        else:
            messages.error(request, 'Please fix the errors below.')

    return render(request, 'codez/register.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('login')


# ─── Main Views ───────────────────────────────────────────────────────────────

@login_required
def home_view(request):
    """Serves the HomePage — problem feed."""
    problems = Problem.objects.all().order_by('-upvotes')[:20]
    context = {
        'problems': problems,
        'user': request.user,
    }
    return render(request, 'codez/home.html', context)


@login_required
def profile_view(request, username=None):
    """Serves the UserProfile page."""
    if username:
        profile_user = get_object_or_404(User, username=username)
    else:
        profile_user = request.user

    profile, _ = UserProfile.objects.get_or_create(user=profile_user)
    context = {
        'profile_user': profile_user,
        'profile': profile,
    }
    return render(request, 'codez/profile.html', context)
