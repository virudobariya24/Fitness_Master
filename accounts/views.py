import random
from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.views.decorators.csrf import ensure_csrf_cookie
from .models import User, ContactMessage, PasswordResetOTP
from .forms import (
    AdminLoginForm,
    AdminCreationForm,
    UserRegistrationForm,
    UserLoginForm,
    ForgotPasswordForm,
    VerifyOTPForm,
    ResetPasswordForm,
    UserProfileUpdateForm,
    UserChangePasswordForm,
)
from packages.models import Packages

AdminModel = get_user_model()


def admin_check(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)


def user_portal_root_view(request):
    """
    Website Root View: Directs visitors directly to the User Dashboard when website is accessed directly (127.0.0.1:8000/).
    - If user has active session, directly opens User Dashboard.
    - If user is not authenticated, redirects to user_dashboard which prompts sign in.
    """
    return redirect('user_dashboard')


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
        request.session.pop('is_user_authenticated', None)
        return redirect('admin_dashboard')

    if request.method == 'POST':
        form = AdminLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            # Clear any conflicting member session flag so admin panel opens cleanly
            request.session.pop('is_user_authenticated', None)
            request.session.pop('user_id', None)
            request.session.pop('user_username', None)
            request.session.pop('user_email', None)
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
            request.session.set_expiry(1209600)  # Persistent session for 14 days
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
    # 1. Validation check for session authentication flag and user ID
    is_authenticated = request.session.get('is_user_authenticated')
    user_id = request.session.get('user_id')

    if not is_authenticated or not user_id:
        messages.warning(request, "Please sign in to access your member dashboard.")
        return redirect('user_login')

    # 2. Validation check against database record
    user = User.objects.filter(pk=user_id).first()
    if not user:
        request.session.pop('is_user_authenticated', None)
        request.session.pop('user_id', None)
        request.session.modified = True
        messages.error(request, "User account could not be validated. Please log in again.")
        return redirect('user_login')

    # 3. Keep session active and persistent across refreshes
    request.session.modified = True

    from packages.models import Order
    packages = Packages.objects.all().order_by('price')
    total_packages = packages.count()
    total_members = User.objects.count()
    total_orders = Order.objects.count()
    total_trainers = AdminModel.objects.filter(is_staff=True).count()

    return render(request, 'accounts/user_dashboard.html', {
        'user': user,
        'packages': packages,
        'is_user_page': True,
        'total_packages': total_packages,
        'total_members': total_members,
        'total_orders': total_orders,
        'total_trainers': total_trainers,
    })


@ensure_csrf_cookie
def user_profile_view(request):
    """
    Dedicated User Profile View for session-authenticated gym members.
    - Displays member account information, registration date, and security status.
    - Supports updating profile details (Name, Username, Email).
    - Supports changing account password securely with current password validation.
    """
    is_authenticated = request.session.get('is_user_authenticated')
    user_id = request.session.get('user_id')

    if not is_authenticated or not user_id:
        messages.warning(request, "Please sign in to access your member profile.")
        return redirect('user_login')

    user = User.objects.filter(pk=user_id).first()
    if not user:
        request.session.pop('is_user_authenticated', None)
        request.session.pop('user_id', None)
        request.session.modified = True
        messages.error(request, "User account could not be validated. Please log in again.")
        return redirect('user_login')

    request.session.modified = True

    profile_form = UserProfileUpdateForm(instance=user, user=user)
    password_form = UserChangePasswordForm(user=user)

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'update_profile':
            profile_form = UserProfileUpdateForm(request.POST, instance=user, user=user)
            if profile_form.is_valid():
                updated_user = profile_form.save()
                # Update session variables
                request.session['user_username'] = updated_user.username
                request.session['user_name'] = updated_user.name or updated_user.username
                request.session['user_email'] = updated_user.email
                request.session.modified = True
                messages.success(request, "Your profile details have been updated successfully!")
                return redirect('user_profile')
            else:
                messages.error(request, "Please correct the errors in your profile details.")
        elif action == 'change_password':
            password_form = UserChangePasswordForm(request.POST, user=user)
            if password_form.is_valid():
                new_pwd = password_form.cleaned_data['new_password']
                user.set_password(new_pwd)
                user.save()
                messages.success(request, "Your password has been changed successfully!")
                return redirect('user_profile')
            else:
                messages.error(request, "Failed to change password. Please check the errors below.")

    return render(request, 'accounts/user_profile.html', {
        'user': user,
        'profile_form': profile_form,
        'password_form': password_form,
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
    Saves inquiries into the ContactMessage model so administrators can view them in Admin Panel.
    """
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        subject = request.POST.get('subject', '').strip()
        message = request.POST.get('message', '').strip()

        if name and email and message:
            ContactMessage.objects.create(
                name=name,
                email=email,
                phone=phone,
                subject=subject if subject else "General Inquiry",
                message=message,
            )
            messages.success(request, f"Thank you, {name}! Your message has been received and forwarded to our fitness team. We will get back to you shortly.")
            return redirect('contact_us')
        else:
            messages.error(request, "Please fill in all required fields (Name, Email, and Message).")

    return render(request, 'pages/contact_us.html', {
        'is_user_page': True,
    })


@login_required(login_url='login')
@user_passes_test(admin_check, login_url='login')
def admin_contact_messages_view(request):
    """
    Admin View for Contact Inquiries.
    Displays all submitted contact messages in the admin panel with search & filter.
    """
    search_query = request.GET.get('q', '').strip()
    status_filter = request.GET.get('status', '').strip()

    messages_qs = ContactMessage.objects.all().order_by('-created_at')

    if search_query:
        messages_qs = messages_qs.filter(
            name__icontains=search_query
        ) | messages_qs.filter(
            email__icontains=search_query
        ) | messages_qs.filter(
            subject__icontains=search_query
        ) | messages_qs.filter(
            message__icontains=search_query
        )

    if status_filter == 'unread':
        messages_qs = messages_qs.filter(is_read=False)
    elif status_filter == 'read':
        messages_qs = messages_qs.filter(is_read=True)

    total_messages = ContactMessage.objects.count()
    unread_messages = ContactMessage.objects.filter(is_read=False).count()

    return render(request, 'accounts/contact_messages_list.html', {
        'contact_messages': messages_qs,
        'total_messages': total_messages,
        'unread_messages': unread_messages,
        'search_query': search_query,
        'status_filter': status_filter,
    })


@login_required(login_url='login')
@user_passes_test(admin_check, login_url='login')
def admin_contact_toggle_read_view(request, pk):
    """Toggle read / unread status for a contact inquiry."""
    contact_msg = get_object_or_404(ContactMessage, pk=pk)
    contact_msg.is_read = not contact_msg.is_read
    contact_msg.save()
    status_str = "Read" if contact_msg.is_read else "Unread"
    messages.success(request, f"Inquiry from {contact_msg.name} marked as {status_str}.")
    return redirect('admin_contact_messages')


@login_required(login_url='login')
@user_passes_test(admin_check, login_url='login')
def admin_contact_delete_view(request, pk):
    """Delete a contact message from the admin panel."""
    contact_msg = get_object_or_404(ContactMessage, pk=pk)
    sender_name = contact_msg.name
    contact_msg.delete()
    messages.success(request, f"Contact message from {sender_name} was deleted successfully.")
    return redirect('admin_contact_messages')


# =============================================================================
# PASSWORD RESET VIA EMAIL OTP (Tasks: Forgot Password, OTP, Reset Password)
# =============================================================================

def send_otp_email(email, otp):
    """
    Sends a 6-digit OTP code to user's registered email using Gmail SMTP.
    Falls back gracefully to printing to console/logs if SMTP or network is restricted.
    """
    subject = "Fitness Master - Password Reset Verification Code"
    plain_message = (
        f"Hello,\n\n"
        f"You recently requested to reset your password for your Fitness Master member account.\n\n"
        f"Your 6-Digit One-Time Password (OTP) is: {otp}\n\n"
        f"This code will expire in 10 minutes.\n"
        f"If you did not request this password reset, please disregard this email.\n\n"
        f"Warm regards,\n"
        f"Fitness Master Support Team"
    )
    html_message = f"""
    <div style="font-family: Arial, sans-serif; max-width: 520px; margin: 0 auto; padding: 24px; border: 1px solid #e2e8f0; border-radius: 12px; background-color: #ffffff;">
        <div style="text-align: center; margin-bottom: 20px;">
            <div style="display: inline-block; background: #0ea5e9; color: #ffffff; width: 48px; height: 48px; border-radius: 10px; line-height: 48px; font-size: 22px; font-weight: bold;">FM</div>
            <h2 style="color: #0f172a; margin: 10px 0 0 0; font-size: 20px; font-weight: 800; letter-spacing: 0.5px;">FITNESS <span style="color: #0ea5e9;">MASTER</span></h2>
            <p style="color: #64748b; font-size: 13px; margin: 4px 0 0 0;">Member Account Security</p>
        </div>
        <hr style="border: none; border-top: 1px solid #f1f5f9; margin: 16px 0;" />
        <p style="color: #334155; font-size: 14px; line-height: 1.6;">Hello,</p>
        <p style="color: #334155; font-size: 14px; line-height: 1.6;">You have requested to reset your password for your Fitness Master account. Use the one-time verification code below to proceed:</p>
        <div style="text-align: center; margin: 28px 0;">
            <div style="display: inline-block; background: #f0fdf4; border: 2px dashed #22c55e; border-radius: 10px; padding: 14px 28px; font-size: 28px; font-weight: 800; letter-spacing: 6px; color: #15803d;">
                {otp}
            </div>
        </div>
        <p style="color: #64748b; font-size: 12px; line-height: 1.5; text-align: center;">
            <strong style="color: #ef4444;">Note:</strong> This OTP is valid for <strong>10 minutes</strong> only. Do not share this code with anyone.
        </p>
        <hr style="border: none; border-top: 1px solid #f1f5f9; margin: 20px 0;" />
        <p style="color: #94a3b8; font-size: 11px; text-align: center; margin: 0;">
            If you did not make this request, you can safely ignore this message.<br />
            Fitness Master Gym & Fitness Club &bull; All Rights Reserved.
        </p>
    </div>
    """

    try:
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'Fitness Master <virajdobariya4@gmail.com>')
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=from_email,
            recipient_list=[email],
            html_message=html_message,
            fail_silently=False,
        )
        print(f"===> [SUCCESS] OTP email successfully dispatched via SMTP to: {email}")
        return True
    except Exception as e:
        print(f"===> [OTP CONSOLE FALLBACK] SMTP dispatch to {email} encountered: {e}")
        print(f"===> [CONSOLE BACKEND OTP]: {otp} for email: {email}")
        return False


@ensure_csrf_cookie
def user_forgot_password_view(request):
    """
    Task (2): User Forgot Password View.
    Allows registered members to request a 6-digit OTP sent to their email.
    """
    if request.session.get('is_user_authenticated'):
        return redirect('user_dashboard')

    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            otp = f"{random.randint(100000, 999999)}"

            # Invalidate older unused OTPs for this email
            PasswordResetOTP.objects.filter(email__iexact=email, is_used=False).update(is_used=True)

            # Create new OTP record
            PasswordResetOTP.objects.create(email=email, otp=otp)

            # Send OTP via email (Gmail SMTP with console fallback)
            send_otp_email(email, otp)

            # Save state in session
            request.session['reset_email'] = email
            request.session['otp_verified'] = False
            request.session.modified = True

            messages.success(request, f"A 6-digit verification code (OTP) has been sent to {email}. Please check your inbox.")
            return redirect('user_verify_otp')
        else:
            messages.error(request, "Please check the email address entered below.")
    else:
        form = ForgotPasswordForm()

    return render(request, 'accounts/user_forgot_password.html', {
        'form': form,
        'is_user_page': True,
    })


@ensure_csrf_cookie
def user_verify_otp_view(request):
    """
    Task (3): User OTP Verification View.
    Validates 6-digit OTP against database and 10-minute expiry window.
    """
    if request.session.get('is_user_authenticated'):
        return redirect('user_dashboard')

    email = request.session.get('reset_email')
    if not email:
        messages.warning(request, "Please enter your registered email address first.")
        return redirect('user_forgot_password')

    # Mask email for safe UI display (e.g. vi***4@gmail.com)
    parts = email.split('@')
    masked_email = email
    if len(parts) == 2:
        uname, domain = parts
        if len(uname) <= 2:
            masked_uname = uname[0] + '*'
        else:
            masked_uname = uname[:2] + '*' * (len(uname) - 3) + uname[-1]
        masked_email = f"{masked_uname}@{domain}"

    if request.method == 'POST':
        form = VerifyOTPForm(request.POST)
        if form.is_valid():
            entered_otp = form.cleaned_data['otp']
            otp_record = PasswordResetOTP.objects.filter(
                email__iexact=email,
                is_used=False
            ).order_by('-created_at').first()

            if otp_record and otp_record.is_valid() and otp_record.otp == entered_otp:
                otp_record.is_verified = True
                otp_record.save()

                request.session['otp_verified'] = True
                request.session.modified = True

                messages.success(request, "OTP verified successfully! Please enter your new password.")
                return redirect('user_reset_password')
            else:
                messages.error(request, "Invalid or expired OTP code. Please enter the correct code or request a new one.")
        else:
            messages.error(request, "Please enter a valid 6-digit numeric OTP.")
    else:
        form = VerifyOTPForm()

    return render(request, 'accounts/user_verify_otp.html', {
        'form': form,
        'email': email,
        'masked_email': masked_email,
        'is_user_page': True,
    })


def user_resend_otp_view(request):
    """
    Resends a fresh 6-digit OTP to the email stored in session.
    """
    email = request.session.get('reset_email')
    if not email:
        messages.warning(request, "Please enter your registered email address first.")
        return redirect('user_forgot_password')

    otp = f"{random.randint(100000, 999999)}"
    PasswordResetOTP.objects.filter(email__iexact=email, is_used=False).update(is_used=True)
    PasswordResetOTP.objects.create(email=email, otp=otp)
    send_otp_email(email, otp)

    messages.info(request, f"A new 6-digit OTP code has been sent to {email}.")
    return redirect('user_verify_otp')


@ensure_csrf_cookie
def user_reset_password_view(request):
    """
    Task (3): User Password Reset View.
    Allows user to set a new password after verifying the OTP.
    """
    if request.session.get('is_user_authenticated'):
        return redirect('user_dashboard')

    email = request.session.get('reset_email')
    otp_verified = request.session.get('otp_verified')

    if not email or not otp_verified:
        messages.warning(request, "Please complete OTP verification before resetting your password.")
        return redirect('user_forgot_password')

    if request.method == 'POST':
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            new_password = form.cleaned_data['new_password']
            user = User.objects.filter(email__iexact=email).first()

            if user:
                user.set_password(new_password)
                user.save()

                # Mark OTP record as used
                PasswordResetOTP.objects.filter(
                    email__iexact=email,
                    is_verified=True,
                    is_used=False
                ).update(is_used=True)

                # Clear reset session state
                request.session.pop('reset_email', None)
                request.session.pop('otp_verified', None)
                request.session.modified = True

                messages.success(request, "Your password has been reset successfully! You can now sign in with your new password.")
                return redirect('user_login')
            else:
                messages.error(request, "Registered user account could not be found.")
                return redirect('user_forgot_password')
        else:
            messages.error(request, "Please ensure passwords match and meet minimum requirements.")
    else:
        form = ResetPasswordForm()

    return render(request, 'accounts/user_reset_password.html', {
        'form': form,
        'email': email,
        'is_user_page': True,
    })

