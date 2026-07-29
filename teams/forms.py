from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import TeamProfile

class TeamRegistrationForm(UserCreationForm):
    # 1. EXPLICITLY REDEFINE USERNAME FIELD TO BYPASS DJANGO'S DEFAULT RESTRICTIONS
    username = forms.CharField(
        max_length=150,
        label="Team Name",
        help_text="Required. 150 characters or fewer. Spaces are allowed."
    )
    
    leader_contact = forms.CharField(
        max_length=150,
        label="Leader Contact (Email)",
        widget=forms.TextInput(attrs={"placeholder": "leader@example.com"}),
    )

    class Meta:
        model = User
        fields = ["username", "leader_contact", "password1", "password2"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Clear password help text
        self.fields["password1"].help_text = None
        self.fields["password2"].help_text = None

    def clean_username(self):
        username = self.cleaned_data.get("username", "").strip()

        if not username:
            raise forms.ValidationError("Please enter a valid team name.")

        # Check for duplicates (case-insensitive)
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError("This team name is already taken.")

        return username

    def save(self, commit=True):
        # Prevent Django model from checking its internal rules on save
        user = super().save(commit=False)
        user.username = self.cleaned_data["username"]
        
        if commit:
            user.save()
            TeamProfile.objects.create(
                user=user,
                leader_contact=self.cleaned_data["leader_contact"],
            )
        return user