from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


# ❌ A02:2021 Cryptographic Failures
class SignUpForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ("username", "email", "password")

    def save(self, commit=True):
        user = super().save(commit=False)

        # ❌ Storing password in plain text
        user.password = self.cleaned_data["password"]

        if commit:
            user.save()

        return user


# ✅ SAFE: Using Django's built-in UserCreationForm
"""
class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = (
            "username",
            "email",
        )

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data.get("email")
        if commit:
            user.save()
        return user
"""
