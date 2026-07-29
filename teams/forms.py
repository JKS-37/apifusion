from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import TeamProfile


class TeamRegistrationForm(UserCreationForm):
    """
    Registration form: Team Name (username), Password, and
    Leader Contact Email/Phone.
    """
    leader_contact = forms.CharField(
        max_length=150,
        label="Leader Contact (Email)",
        widget=forms.TextInput(attrs={"placeholder": "leader@example.com"}),
    )

    class Meta:
        model = User
        fields = ["username", "leader_contact", "password1", "password2"]
        labels = {"username": "Team Name"}

    def clean_username(self):
        username = self.cleaned_data["username"].strip()
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
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["password1"].help_text = None
        self.fields["password2"].help_text = None
