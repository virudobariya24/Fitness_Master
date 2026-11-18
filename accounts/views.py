from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib import messages
from .forms import UserRegistrationForm, UserLoginForm, UserProfileUpdateForm
from .models import UserProfile


@ensure_csrf_cookie
def register_view(request):
    """User Registration with role USER and automatic Profile creation."""
    if request.user.is_authenticated:
        return redirect('user_dashboard')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(
                request,
                f"Account created successfully for {user.first_name or user.username}! Please sign in with your credentials to access your dashboard."
            )
            return redirect('login')
        else:
            messages.error(request, "Please resolve the errors below to complete your registration.")
    else:
        form = UserRegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})


@ensure_csrf_cookie
def login_view(request):
    """Login view supporting redirection based on user role."""
    if request.user.is_authenticated:
        if request.user.is_admin_user():
            return redirect('admin_dashboard')
        return redirect('user_dashboard')

    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user.is_blocked:
                messages.error(request, "Your account has been deactivated. Please contact Fitness Master support.")
                return render(request, 'accounts/login.html', {'form': form})

            login(request, user)
            messages.success(request, f"Welcome back, {user.first_name or user.username}!")
            
            # Check redirect
            next_url = request.GET.get('next') or request.POST.get('next')
            if next_url and next_url.startswith('/'):
                return redirect(next_url)

            if user.is_admin_user():
                return redirect('admin_dashboard')
            return redirect('user_dashboard')
        else:
            messages.error(request, "Invalid username or password. Please try again.")
    else:
        form = UserLoginForm()

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    """Logout view."""
    if request.user.is_authenticated:
        logout(request)
        messages.info(request, "You have been logged out successfully. Stay disciplined!")
    return redirect('home')


@login_required(login_url='login')
def profile_view(request):
    """View and update profile information."""
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = UserProfileUpdateForm(request.POST, request.FILES, instance=profile)
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        
        if form.is_valid():
            form.save()
            if first_name or last_name:
                request.user.first_name = first_name
                request.user.last_name = last_name
                request.user.save()
            messages.success(request, "Your profile details have been successfully updated!")
            return redirect('user_profile')
        else:
            messages.error(request, "Please correct the form errors.")
    else:
        form = UserProfileUpdateForm(instance=profile)

    context = {
        'profile': profile,
        'form': form,
    }
    return render(request, 'accounts/profile.html', context)
