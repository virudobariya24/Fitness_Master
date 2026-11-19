from django import forms
from .models import Packages


class PackageForm(forms.ModelForm):
    class Meta:
        model = Packages
        fields = [
            'title', 'price', 'duration', 'access_hours',
            'instruments', 'classes_per_week', 'membership_duration',
            'drinking_package', 'personal_instructor'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Gold Pro Membership',
                'required': True
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': 'e.g. 1999.00',
                'required': True
            }),
            'duration': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. 1 Month, 3 Months, 1 Year',
                'required': True
            }),
            'access_hours': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. 24/7 Access or 6:00 AM - 10:00 PM',
                'required': True
            }),
            'instruments': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'e.g. Full Cardio, Dumbbells, Olympic Barbells, CrossFit Rig',
                'required': True
            }),
            'classes_per_week': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. 4 Classes/Week or Unlimited',
                'required': True
            }),
            'membership_duration': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Monthly, Quarterly, Annual',
                'required': True
            }),
            'drinking_package': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Hydration Bar & Protein Shakes Included',
                'required': True
            }),
            'personal_instructor': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. 1-on-1 Dedicated Trainer Included',
                'required': True
            }),
        }
