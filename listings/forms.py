from django import forms

from .models import Comment, InspectionRequest, Property, PropertyImage, Report, Review


class PropertySearchForm(forms.Form):
    keyword = forms.CharField(
        required=False, label="Keyword",
        widget=forms.TextInput(attrs={"placeholder": "e.g. self contain, duplex, near mall..."}),
    )
    category = forms.ChoiceField(
        required=False, label="Category",
        choices=[("", "Any category")] + list(Property.CATEGORY_CHOICES),
    )
    state = forms.ModelChoiceField(queryset=None, required=False, empty_label="Any state")
    area = forms.CharField(
        required=False, label="Area / Neighbourhood",
        widget=forms.TextInput(attrs={"placeholder": "e.g. Wuse II, Lekki...", "list": "areaSuggestions"}),
    )
    property_type = forms.CharField(
        required=False, label="Property type",
        widget=forms.TextInput(attrs={"placeholder": "e.g. 2 Bedroom, Duplex...", "list": "propertyTypeSuggestions"}),
    )
    min_budget = forms.DecimalField(required=False, min_value=0, label="Min budget (₦)")
    max_budget = forms.DecimalField(required=False, min_value=0, label="Max budget (₦)")
    verified_only = forms.BooleanField(required=False, label="Verified listings only")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from .models import State

        self.fields["state"].queryset = State.objects.all()
        for name, field in self.fields.items():
            css = "form-check-input" if isinstance(field, forms.BooleanField) else "form-control"
            field.widget.attrs.setdefault("class", css)


class PropertyForm(forms.ModelForm):
    class Meta:
        model = Property
        fields = [
            "category", "title", "description", "property_type", "state", "area", "address_note",
            "facilities", "latitude", "longitude", "price", "price_period", "bedrooms", "bathrooms",
            "video_url",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 5}),
            "facilities": forms.TextInput(attrs={
                "placeholder": "e.g. Water, 24hr Electricity, Parking, Security, POP Ceiling",
            }),
            "latitude": forms.HiddenInput(),
            "longitude": forms.HiddenInput(),
            "property_type": forms.TextInput(attrs={
                "list": "propertyTypeSuggestions",
                "placeholder": 'e.g. "2 Bedroom Flat", "Self Contain", "Duplex"',
            }),
            "area": forms.TextInput(attrs={
                "list": "areaSuggestions",
                "placeholder": "e.g. Wuse II, Lekki Phase 1...",
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name not in ("latitude", "longitude"):
                field.widget.attrs.setdefault("class", "form-control")


class PropertyImageForm(forms.ModelForm):
    class Meta:
        model = PropertyImage
        fields = ["image", "caption"]
        widgets = {
            "image": forms.ClearableFileInput(attrs={"accept": "image/*", "class": "image-input"}),
        }


PropertyImageFormSet = forms.inlineformset_factory(
    Property, PropertyImage, form=PropertyImageForm, extra=5, max_num=8, can_delete=True
)


class InspectionRequestForm(forms.ModelForm):
    class Meta:
        model = InspectionRequest
        fields = ["full_name", "phone_number", "email", "preferred_date", "message"]
        widgets = {
            "preferred_date": forms.DateInput(attrs={"type": "date"}),
            "message": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")


class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ["reporter_name", "reporter_contact", "reason", "details"]
        widgets = {
            "details": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["rating", "comment"]
        widgets = {
            "rating": forms.Select(choices=[(i, f"{i} star{'s' if i > 1 else ''}") for i in range(1, 6)]),
            "comment": forms.Textarea(attrs={"rows": 3, "placeholder": "Share your experience with this agent..."}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["text"]
        widgets = {
            "text": forms.Textarea(attrs={
                "rows": 2, "placeholder": "Ask a question or leave a note about this listing...",
                "class": "form-control",
            }),
        }
