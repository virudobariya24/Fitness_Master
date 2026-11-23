from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.views.decorators.csrf import ensure_csrf_cookie
from .models import User
from .forms import AdminLoginForm, AdminCreationForm, UserRegistrationForm, UserLoginForm
from packages.models import Packages

AdminModel = get_user_model()


def admin_check(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)


def user_portal_root_view(request):
    """
    Website Root View: Directs visitors directly to the User Panel when website is accessed directly.
    - If user has active session, redirects to user_dashboard.
    - Otherwise, redirects to packages_cards (Public User Packages Catalog with 'View More' buttons).
    """
    if request.session.get('is_user_authenticated'):
        return redirect('user_dashboard')
    return redirect('packages_cards')


def admin_gateway_view(request):
    """
    Admin Gateway View: Triggered when user enters .../admin or .../admin/ in the URL.
    - If admin is already authenticated: directly opens Admin Dashboard (admin_dashboard).
    - If admin is not authenticated or submitting login form: opens custom Admin Login page.
    """
    if request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser):
        return redirect('admin_dashboard')
    return admin_login_view(request)


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

    return render(request, 'accounts/login.html', {'form': form, 'is_auth_page': True})


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


@login_required(login_url='login')
@user_passes_test(admin_check, login_url='login')
def admin_registered_users_view(request):
    """
    Admin View for Registered Users (Custom User Model data).
    Displays registered users/members in the admin panel with search & details.
    """
    search_query = request.GET.get('q', '').strip()
    users_qs = User.objects.all().order_by('-created_at')
    if search_query:
        users_qs = users_qs.filter(
            username__icontains=search_query
        ) | users_qs.filter(
            name__icontains=search_query
        ) | users_qs.filter(
            email__icontains=search_query
        )

    return render(request, 'accounts/registered_users_list.html', {
        'users': users_qs,
        'total_users': User.objects.count(),
        'search_query': search_query,
    })


@ensure_csrf_cookie
def user_register_view(request):
    """
    Task (2): User Registration View.
    Renders registration form with fields: username, email, and password.
    Saves validated users into the custom User model with hashed passwords.
    """
    if request.session.get('is_user_authenticated'):
        return redirect('user_dashboard')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            messages.success(request, f"Registration successful for '{new_user.username}'! You can now sign in.")
            return redirect('user_login')
        else:
            messages.error(request, "Registration failed. Please check the errors below.")
    else:
        form = UserRegistrationForm()

    return render(request, 'accounts/user_register.html', {'form': form, 'is_user_page': True})


@ensure_csrf_cookie
def user_login_view(request):
    """
    Task (3): User Login View using Django Sessions.
    Authenticates against custom User model and stores user session in request.session.
    """
    if request.session.get('is_user_authenticated'):
        return redirect('user_dashboard')

    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            user = form.get_user()
            # Set Django Session Keys for User Login (Task 3)
            request.session['user_id'] = user.id
            request.session['user_username'] = user.username
            request.session['user_name'] = user.name or user.username
            request.session['user_email'] = user.email
            request.session['is_user_authenticated'] = True
            request.session.modified = True
            messages.success(request, f"Welcome back, {user.name or user.username}!")
            return redirect('user_dashboard')
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = UserLoginForm()

    return render(request, 'accounts/user_login.html', {'form': form, 'is_user_page': True})


def user_logout_view(request):
    """
    Task (3): User Logout View using Django Sessions.
    Terminates user session and clears all session data.
    """
    request.session.pop('user_id', None)
    request.session.pop('user_username', None)
    request.session.pop('user_name', None)
    request.session.pop('user_email', None)
    request.session.pop('is_user_authenticated', None)
    request.session.modified = True
    messages.info(request, "You have been logged out successfully from your user account.")
    return redirect('user_login')


def user_dashboard_view(request):
    """
    User Dashboard for session-authenticated users.
    Displays user account details, active packages catalog with 'View More' links.
    Validates session state, user ID, and active database credentials.
    """
    # 1. Validation check for session authentication flag
    if not request.session.get('is_user_authenticated'):
        messages.warning(request, "Please sign in to access your member dashboard.")
        return redirect('user_login')

    # 2. Validation check for user ID in session
    user_id = request.session.get('user_id')
    if not user_id:
        request.session.flush()
        messages.warning(request, "Session expired or invalid. Please sign in again.")
        return redirect('user_login')

    # 3. Validation check against database record
    user = User.objects.filter(pk=user_id).first()
    if not user:
        request.session.flush()
        messages.error(request, "User account could not be validated. Please log in again.")
        return redirect('user_login')

    packages = Packages.objects.all().order_by('price')
    return render(request, 'accounts/user_dashboard.html', {
        'user': user,
        'packages': packages,
        'is_user_page': True,
    })


def about_us_view(request):
    """
    Public and Member About Us page.
    Renders gym story, facilities, stats, trainers, and fitness mission.
    """
    return render(request, 'pages/about_us.html', {
        'is_user_page': True,
    })


def contact_us_view(request):
    """
    Public and Member Contact Us page.
    Renders contact info, map preview, operating hours, and interactive message form.
    """
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        subject = request.POST.get('subject', '').strip()
        message = request.POST.get('message', '').strip()

        if name and email and message:
            messages.success(request, f"Thank you, {name}! Your message has been sent successfully. Our team will get back to you shortly.")
            return redirect('contact_us')
        else:
            messages.error(request, "Please fill in all required fields (Name, Email, and Message).")

    return render(request, 'pages/contact_us.html', {
        'is_user_page': True,
    })
