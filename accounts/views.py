from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.views.decorators.csrf import ensure_csrf_cookie
from .forms import AdminLoginForm, AdminCreationForm

AdminModel = get_user_model()


def admin_check(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)


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


@login_required(login_url='login')
@user_passes_test(admin_check, login_url='login')
def admin_accounts_view(request):
    """
    Dedicated Page for Option 3: Admin Accounts Management.
    Lists all Admin model users, showing usernames, emails, roles, and status.
    Supports creating a new admin account via form modal.
    """
    admins = AdminModel.objects.all().order_by('-date_joined')
    form = AdminCreationForm()

    if request.method == 'POST':
        form = AdminCreationForm(request.POST)
        if form.is_valid():
            new_admin = form.save()
            messages.success(request, f"New Administrator '{new_admin.username}' created successfully!")
            return redirect('admin_accounts')
        else:
            messages.error(request, "Failed to create administrator. Please check the form errors.")

    return render(request, 'accounts/admin_list.html', {
        'admins': admins,
        'form': form,
        'total_admins': admins.count(),
        'superusers_count': admins.filter(is_superuser=True).count(),
    })
