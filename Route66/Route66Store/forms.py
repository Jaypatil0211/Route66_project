from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Review


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Email address")
    first_name = forms.CharField(max_length=50, required=True, label="First name")
    last_name = forms.CharField(max_length=50, required=True, label="Last name")

    class Meta:
        model = User
        # Only show the requested fields to the user.
        fields = ('first_name', 'last_name', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove username from the rendered fields, we'll set it from email.
        self.fields.pop('username', None)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("An account with this email already exists.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        email = self.cleaned_data.get('email')
        user.email = email
        # Use email as the username so login can work with the email value.
        user.username = email
        user.first_name = self.cleaned_data.get('first_name', '')
        user.last_name = self.cleaned_data.get('last_name', '')
        if commit:
            user.save()
        return user


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ('rating', 'title', 'body')
        widgets = {
            'rating': forms.RadioSelect(choices=[(i, f'{i} Star{"s" if i > 1 else ""}') for i in range(1, 6)]),
            'body': forms.Textarea(attrs={'rows': 4}),
        }


class CheckoutForm(forms.Form):
    first_name = forms.CharField(max_length=50)
    last_name = forms.CharField(max_length=50)
    email = forms.EmailField()
    phone = forms.CharField(max_length=20)
    shipping_address = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}))
    city = forms.CharField(max_length=100)
    state = forms.CharField(max_length=100)
    zip_code = forms.CharField(max_length=20)
    country = forms.CharField(max_length=100, initial='India')
    notes = forms.CharField(widget=forms.Textarea(attrs={'rows': 2}), required=False)
