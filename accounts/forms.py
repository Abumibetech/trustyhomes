from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from agents.models import AgentProfile


class StyledUserCreationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")


class TenantSignUpForm(StyledUserCreationForm):
    """A plain account for people searching for a place to rent — can save
    favourites, leave reviews, and get notified about their inspection requests."""

    email = forms.EmailField(required=True)
    phone_number = forms.CharField(max_length=20, required=False, label="Phone number (optional)")

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]


class AgentSignUpForm(StyledUserCreationForm):
    business_name = forms.CharField(max_length=150, required=True, label="Business / full name")
    whatsapp_number = forms.CharField(
        max_length=20,
        required=True,
        label="WhatsApp number",
        help_text="Include country code, e.g. 2348012345678",
    )
    account_type = forms.ChoiceField(choices=AgentProfile.ACCOUNT_TYPE_CHOICES, label="I am a")
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            AgentProfile.objects.create(
                user=user,
                business_name=self.cleaned_data["business_name"],
                whatsapp_number=self.cleaned_data["whatsapp_number"],
                account_type=self.cleaned_data["account_type"],
            )
        return user


class BecomeAgentForm(forms.ModelForm):
    """
    For a user who's already logged in (as a tenant, or as a superuser) and
    wants to start listing properties on their EXISTING account — no new
    username/password needed, just the agent-specific details.
    """

    class Meta:
        model = AgentProfile
        fields = ["account_type", "business_name", "whatsapp_number", "phone_number", "bio"]
        widgets = {"bio": forms.Textarea(attrs={"rows": 3})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")
