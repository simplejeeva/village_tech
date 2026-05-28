import re
from datetime import timedelta

from django import forms
from django.utils import timezone

from customers.models import Customer

DEDUPE_WINDOW = timedelta(seconds=60)
_NON_DIGIT = re.compile(r"\D+")


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ("name", "phone", "place", "notes")
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control vt-input",
                    "placeholder": "Your name",
                    "autocomplete": "name",
                    "required": True,
                }
            ),
            "phone": forms.TextInput(
                attrs={
                    "class": "form-control vt-input",
                    "placeholder": "10-digit mobile number",
                    "inputmode": "tel",
                    "autocomplete": "tel",
                    "required": True,
                }
            ),
            "place": forms.TextInput(
                attrs={
                    "class": "form-control vt-input",
                    "placeholder": "Area or locality",
                    "autocomplete": "address-level2",
                    "required": True,
                }
            ),
            "notes": forms.Textarea(
                attrs={
                    "class": "form-control vt-input vt-textarea",
                    "placeholder": "What do you usually buy?",
                    "rows": 3,
                    "style": "height: 110px;",
                    "maxlength": 500,
                }
            ),
        }
        labels = {
            "name": "Name",
            "phone": "Phone",
            "place": "Place / Area",
            "notes": "What you usually buy",
        }

    def clean_name(self) -> str:
        value = (self.cleaned_data.get("name") or "").strip()
        if not value:
            raise forms.ValidationError("Please enter your name.")
        return value

    def clean_place(self) -> str:
        value = (self.cleaned_data.get("place") or "").strip()
        if not value:
            raise forms.ValidationError("Please tell us your area.")
        return value

    def clean_phone(self) -> str:
        raw = self.cleaned_data.get("phone") or ""
        digits = _NON_DIGIT.sub("", raw)
        # Drop a leading country code "91" if present and length is 12
        if len(digits) == 12 and digits.startswith("91"):
            digits = digits[2:]
        if len(digits) != 10:
            raise forms.ValidationError(
                "Please enter a valid 10-digit mobile number."
            )
        return digits

    def save(self, commit: bool = True) -> Customer:
        # Soft dedupe: if a row with same phone + place exists within the last
        # 60 seconds, return that one instead of creating a duplicate.
        phone = self.cleaned_data["phone"]
        place = self.cleaned_data["place"]
        cutoff = timezone.now() - DEDUPE_WINDOW
        existing = (
            Customer.objects.filter(
                phone=phone, place=place, created_at__gte=cutoff
            )
            .order_by("-created_at")
            .first()
        )
        if existing is not None:
            return existing
        return super().save(commit=commit)
