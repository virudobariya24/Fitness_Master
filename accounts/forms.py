from django import forms
from django.contrib.auth import get_user_model, authenticate
from django.db.models import Q
from .models import UserProfile

User = get_user_model()


class UserRegistrationForm(forms.Form):
    """User Registration Form with First Name, Last Name, Email, Password, Confirm Password."""
    first_name = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 rounded-xl border border-[#DCE2EA] bg-[#F8FAFC] focus:bg-white focus:border-[#06B6D4] focus:ring-2 focus:ring-[#06B6D4]/30 focus:outline-none transition text-sm font-semibold text-[#0F172A]',
            'placeholder': 'First Name'
        })
    )
    last_name = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 rounded-xl border border-[#DCE2EA] bg-[#F8FAFC] focus:bg-white focus:border-[#06B6D4] focus:ring-2 focus:ring-[#06B6D4]/30 focus:outline-none transition text-sm font-semibold text-[#0F172A]',
            'placeholder': 'Last Name'
        })
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-3 rounded-xl border border-[#DCE2EA] bg-[#F8FAFC] focus:bg-white focus:border-[#06B6D4] focus:ring-2 focus:ring-[#06B6D4]/30 focus:outline-none transition text-sm font-semibold text-[#0F172A]',
            'placeholder': 'name@example.com'
        })
    )
    password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 rounded-xl border border-[#DCE2EA] bg-[#F8FAFC] focus:bg-white focus:border-[#06B6D4] focus:ring-2 focus:ring-[#06B6D4]/30 focus:outline-none transition text-sm font-semibold text-[#0F172A]',
            'placeholder': 'Create password'
        })
    )
    confirm_password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 rounded-xl border border-[#DCE2EA] bg-[#F8FAFC] focus:bg-white focus:border-[#06B6D4] focus:ring-2 focus:ring-[#06B6D4]/30 focus:outline-none transition text-sm font-semibold text-[#0F172A]',
            'placeholder': 'Confirm password'
        })
    )

    # Optional fields for backward compatibility
    password1 = forms.CharField(required=False, widget=forms.PasswordInput)
    password2 = forms.CharField(required=False, widget=forms.PasswordInput)
    username = forms.CharField(required=False)
    fitness_goal = forms.CharField(required=False)

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email address already exists.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        pwd = cleaned_data.get('password') or cleaned_data.get('password1')
        conf = cleaned_data.get('confirm_password') or cleaned_data.get('password2')

        if not pwd:
            self.add_error('password', "Please enter a password.")
        elif len(pwd) < 6:
            self.add_error('password', "Password must contain at least 6 characters.")

        if not conf:
            self.add_error('confirm_password', "Please confirm your password.")

        if pwd and conf and pwd != conf:
            self.add_error('confirm_password', "Passwords do not match. Please verify.")

        cleaned_data['final_password'] = pwd
        return cleaned_data

    def save(self):
        email = self.cleaned_data['email']
        first_name = self.cleaned_data['first_name']
        last_name = self.cleaned_data['last_name']
        password = self.cleaned_data['final_password']
        goal = self.cleaned_data.get('fitness_goal') or ''

        # Use explicitly provided username or generate from email
        custom_u = self.cleaned_data.get('username')
        if custom_u and not User.objects.filter(username__iexact=custom_u).exists():
            uname = custom_u
        else:
            uname = email.lower()
            if User.objects.filter(username__iexact=uname).exists():
                uname = f"{email.split('@')[0]}_{User.objects.count() + 1}"

        user = User.objects.create_user(
            username=uname,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            role='USER'
        )
        if goal:
            profile = user.profile
            profile.fitness_goal = goal
            profile.save()
        return user


class UserLoginForm(forms.Form):
    """Login Form allowing authentication via Username OR Email address."""
    username = forms.CharField(
        label="Username or Email",
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 rounded-xl border border-[#DCE2EA] bg-[#F8FAFC] focus:bg-white focus:border-[#06B6D4] focus:ring-2 focus:ring-[#06B6D4]/30 focus:outline-none transition text-sm font-semibold text-[#0F172A]',
            'placeholder': 'Username or email address',
            'autofocus': True,
        })
    )
    password = forms.CharField(
        label="Password",
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 rounded-xl border border-[#DCE2EA] bg-[#F8FAFC] focus:bg-white focus:border-[#06B6D4] focus:ring-2 focus:ring-[#06B6D4]/30 focus:outline-none transition text-sm font-semibold text-[#0F172A]',
            'placeholder': 'Enter your password'
        })
    )

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user_cache = None
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        identifier = cleaned_data.get('username', '').strip()
        pwd = cleaned_data.get('password', '')

        if identifier and pwd:
            # Look up by either username or email
            user_obj = User.objects.filter(
                Q(username__iexact=identifier) | Q(email__iexact=identifier)
            ).first()

            actual_username = user_obj.username if user_obj else identifier
            user = authenticate(self.request, username=actual_username, password=pwd)

            if user is None:
                raise forms.ValidationError("Invalid username/email or password. Please try again.")

            if user.is_blocked:
                raise forms.ValidationError("Your account has been deactivated. Please contact support.")

            self.user_cache = user
        return cleaned_data

    def get_user(self):
        return self.user_cache


class UserProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = [
            'phone', 'gender', 'age', 'height', 'current_weight', 'target_weight',
            'fitness_goal', 'activity_level', 'daily_water_goal', 'daily_calorie_goal',
            'profile_picture', 'bio'
        ]
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'w-full px-4 py-2.5 rounded-xl border border-[#DCE2EA] bg-white focus:border-[#06B6D4] focus:outline-none text-xs font-semibold', 'placeholder': 'e.g. +1 234 567 8900'}),
            'gender': forms.Select(attrs={'class': 'w-full px-4 py-2.5 rounded-xl border border-[#DCE2EA] bg-white focus:border-[#06B6D4] focus:outline-none text-xs font-semibold'}),
            'age': forms.NumberInput(attrs={'class': 'w-full px-4 py-2.5 rounded-xl border border-[#DCE2EA] bg-white focus:border-[#06B6D4] focus:outline-none text-xs font-semibold', 'placeholder': 'e.g. 25'}),
            'height': forms.NumberInput(attrs={'class': 'w-full px-4 py-2.5 rounded-xl border border-[#DCE2EA] bg-white focus:border-[#06B6D4] focus:outline-none text-xs font-semibold', 'step': '0.1', 'placeholder': 'e.g. 175.0'}),
            'current_weight': forms.NumberInput(attrs={'class': 'w-full px-4 py-2.5 rounded-xl border border-[#DCE2EA] bg-white focus:border-[#06B6D4] focus:outline-none text-xs font-semibold', 'step': '0.1', 'placeholder': 'e.g. 70.0'}),
            'target_weight': forms.NumberInput(attrs={'class': 'w-full px-4 py-2.5 rounded-xl border border-[#DCE2EA] bg-white focus:border-[#06B6D4] focus:outline-none text-xs font-semibold', 'step': '0.1', 'placeholder': 'e.g. 65.0'}),
            'fitness_goal': forms.Select(attrs={'class': 'w-full px-4 py-2.5 rounded-xl border border-[#DCE2EA] bg-white focus:border-[#06B6D4] focus:outline-none text-xs font-semibold'}),
            'activity_level': forms.Select(attrs={'class': 'w-full px-4 py-2.5 rounded-xl border border-[#DCE2EA] bg-white focus:border-[#06B6D4] focus:outline-none text-xs font-semibold'}),
            'daily_water_goal': forms.NumberInput(attrs={'class': 'w-full px-4 py-2.5 rounded-xl border border-[#DCE2EA] bg-white focus:border-[#06B6D4] focus:outline-none text-xs font-semibold', 'placeholder': 'e.g. 2500'}),
            'daily_calorie_goal': forms.NumberInput(attrs={'class': 'w-full px-4 py-2.5 rounded-xl border border-[#DCE2EA] bg-white focus:border-[#06B6D4] focus:outline-none text-xs font-semibold', 'placeholder': 'e.g. 2200'}),
            'bio': forms.Textarea(attrs={'class': 'w-full px-4 py-2.5 rounded-xl border border-[#DCE2EA] bg-white focus:border-[#06B6D4] focus:outline-none text-xs font-semibold', 'rows': 3, 'placeholder': 'Tell us about your fitness motivation and background...'}),
            'profile_picture': forms.FileInput(attrs={'class': 'w-full px-4 py-2 rounded-xl border border-[#DCE2EA] bg-white text-xs text-[#667085]'}),
        }
