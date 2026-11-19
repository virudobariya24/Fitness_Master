from django import forms
from django.contrib.auth import authenticate, get_user_model

AdminModel = get_user_model()


class AdminLoginForm(forms.Form):
    """Admin Login Form with Bootstrap 5 styling."""
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Enter admin username or email',
            'autofocus': True,
            'id': 'adminUsername',
            'required': True
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg',
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
