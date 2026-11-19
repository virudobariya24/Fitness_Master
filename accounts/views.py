from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib import messages
from django.views.decorators.csrf import ensure_csrf_cookie
from .forms import AdminLoginForm


@ensure_csrf_cookie
def admin_login_view(request):
    """
    Task (1): Admin Login View using Django Authentication System.
    Redirects to admin dashboard upon successful authentication.
    """
    if request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser):
        return redirect('admin_dashboard')

    if request.method == 'POST':
        form = AdminLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, Administrator {user.username}!")
            return redirect('admin_dashboard')
        else:
            messages.error(request, "Invalid administrator credentials.")
    else:
        form = AdminLoginForm()

    return render(request, 'accounts/login.html', {'form': form})


def admin_logout_view(request):
    """
    Task (1): Admin Logout View using Django Authentication System.
    Terminates session and redirects to login page.
    """
    if request.user.is_authenticated:
        logout(request)
        messages.info(request, "You have been logged out successfully from the Admin Portal.")
    return redirect('login')
