from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import TeamProfile


class TeamRegistrationForm(UserCreationForm):
    leader_contact = forms.CharField(
        max_length=150,
        label="Leader Contact (Email)",
        widget=forms.TextInput(attrs={"placeholder": "leader@example.com or +91XXXXXXXXXX"}),
    )

    class Meta:
        model = User
        fields = ["username", "leader_contact", "password1", "password2"]
        labels = {"username": "Team Name"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 1. Clear password help text
        self.fields["password1"].help_text = None
        self.fields["password2"].help_text = None

        # 2. CLEAR BUILT-IN USERNAME VALIDATORS TO ALLOW SPACES
        self.fields["username"].validators = []
        self.fields["username"].help_text = "Required. 150 characters or fewer."

    def clean_username(self):
        username = self.cleaned_data.get("username", "").strip()

        if not username:
            raise forms.ValidationError("Please enter a valid team name.")

        # Check for duplicate usernames (case-insensitive)
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError("This team name is already taken.")

        return username

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            TeamProfile.objects.create(
                user=user,
                leader_contact=self.cleaned_data["leader_contact"],
            )
        return user