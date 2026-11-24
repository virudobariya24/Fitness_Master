from django import forms
from django.contrib.auth import authenticate, get_user_model
from .models import User

AdminModel = get_user_model()


class AdminLoginForm(forms.Form):
    """Admin Login Form with Bootstrap 5 styling."""
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control py-2.5',
            'placeholder': 'Enter admin username or email',
            'autofocus': True,
            'id': 'adminUsername',
            'required': True
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control py-2.5',
            'placeholder': 'Enter admin password',
            'id': 'adminPassword',
            'required': True
        })
    )

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user_cache = None
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username', '').strip()
        password = cleaned_data.get('password', '')

        if username and password:
            # 1. Attempt standard authentication by username
            user = authenticate(self.request, username=username, password=password)

            # 2. If not matched, attempt by email
            if user is None:
                matched = AdminModel.objects.filter(email__iexact=username).first()
                if matched:
                    user = authenticate(self.request, username=matched.username, password=password)

            if user is None:
                raise forms.ValidationError("Invalid admin credentials. Please verify your username and password.")

            if not user.is_staff and not user.is_superuser:
                raise forms.ValidationError("Access denied. The specified account does not possess administrator privileges.")

            self.user_cache = user
        return cleaned_data

    def get_user(self):
        return self.user_cache


class AdminCreationForm(forms.ModelForm):
    """Form to create a new Administrator account."""
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter strong admin password',
            'required': True
        }),
        help_text="Password will be securely hashed using PBKDF2."
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm password',
            'required': True
        })
    )

    class Meta:
        model = AdminModel
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter admin username',
                'required': True
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'admin@fitnessmaster.com',
                'required': True
            }),
        }

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if AdminModel.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError("An admin account with this username already exists.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if AdminModel.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An admin account with this email address already exists.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("The passwords entered do not match.")
        return cleaned_data

    def save(self, commit=True):
        admin_user = super().save(commit=False)
        admin_user.set_password(self.cleaned_data['password'])
        admin_user.is_staff = True
        admin_user.is_superuser = True
        if commit:
            admin_user.save()
        return admin_user


class UserRegistrationForm(forms.ModelForm):
    """
    Task (2): User Registration Form with fields: username, email, and password.
    Saves new users into the custom User model with PBKDF2 hashed passwords.
    """
    name = forms.CharField(
        max_length=150,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your full name (optional)',
            'id': 'regName'
        })
    )
    username = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Choose a unique username',
            'id': 'regUsername',
            'required': True
        })
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'name@example.com',
            'id': 'regEmail',
            'required': True
        })
    )
    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Create a strong password',
            'id': 'regPassword',
            'required': True
        }),
        help_text="Password will be encrypted using PBKDF2 algorithm."
    )
    confirm_password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Re-enter your password',
            'id': 'regConfirmPassword',
            'required': True
        })
    )

    class Meta:
        model = User
        fields = ['username', 'name', 'email', 'password']

    def clean_username(self):
        username = self.cleaned_data.get('username', '').strip()
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError("This username is already taken. Please choose another username.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email address already exists.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match. Please re-enter identical passwords.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        if not user.name:
            user.name = user.username
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class UserLoginForm(forms.Form):
    """
    Task (3): User Login Form for authentication using Django sessions.
    Validates credentials against custom User model.
    """
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control py-2.5',
            'placeholder': 'Enter your username or email',
            'id': 'userLoginUsername',
            'required': True,
            'autofocus': True
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control py-2.5',
            'placeholder': 'Enter your password',
            'id': 'userLoginPassword',
            'required': True
        })
    )

    def __init__(self, *args, **kwargs):
        self.user_cache = None
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username', '').strip()
        password = cleaned_data.get('password', '')

        if username and password:
            user = User.objects.filter(username__iexact=username).first()
            if not user:
                user = User.objects.filter(email__iexact=username).first()

            if not user or not user.check_password(password):
                raise forms.ValidationError("Invalid username or password. Please try again.")

            self.user_cache = user
        return cleaned_data

    def get_user(self):
        return self.user_cache


class ForgotPasswordForm(forms.Form):
    """
    Forgot Password Form: Prompts member for their registered email address.
    Validates that a User record exists for this email.
    """
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control py-2.5',
            'placeholder': 'Enter your registered email (e.g. member@fitnessmaster.com)',
            'id': 'forgotEmail',
            'required': True,
            'autofocus': True
        }),
        label="Registered Email Address"
    )

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if not User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("No registered member account was found with this email address.")
        return email


class VerifyOTPForm(forms.Form):
    """
    OTP Verification Form: Accepts 6-digit numeric OTP.
    """
    otp = forms.CharField(
        max_length=6,
        min_length=6,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control py-2.5 text-center fw-bold fs-4',
            'placeholder': '123456',
            'id': 'otpInput',
            'maxlength': '6',
            'pattern': '[0-9]{6}',
            'inputmode': 'numeric',
            'autocomplete': 'one-time-code',
            'required': True,
            'autofocus': True,
            'style': 'letter-spacing: 0.35rem;'
        }),
        label="6-Digit OTP"
    )

    def clean_otp(self):
        otp = self.cleaned_data.get('otp', '').strip()
        if not otp.isdigit() or len(otp) != 6:
            raise forms.ValidationError("Please enter a valid 6-digit numeric OTP code.")
        return otp


class ResetPasswordForm(forms.Form):
    """
    Password Reset Form: Allows member to enter and confirm new password.
    """
    new_password = forms.CharField(
        min_length=6,
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control py-2.5',
            'placeholder': 'Enter your new password (min. 6 characters)',
            'id': 'newPasswordInput',
            'required': True,
            'autofocus': True
        }),
        label="New Password",
        help_text="Password must contain at least 6 characters."
    )
    confirm_password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control py-2.5',
            'placeholder': 'Re-enter your new password to confirm',
            'id': 'confirmPasswordInput',
            'required': True
        }),
        label="Confirm New Password"
    )

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')

        if new_password and confirm_password and new_password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match. Please re-enter identical passwords.")
        return cleaned_data

