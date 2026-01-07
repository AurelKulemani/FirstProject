from django import forms
from django.utils import timezone
from django.utils.translation import get_language

from .models import Appointment, Service


def _t(en: str, sq: str) -> str:
    """Tiny helper for bilingual (EN/SQ) messages without .po files."""
    lang = (get_language() or "en").lower()
    return sq if lang.startswith("sq") else en

class ContactForm(forms.Form):
    name = forms.CharField(max_length=120, widget=forms.TextInput(attrs={
        "class": "form-control",
        "placeholder": "Your name",
    }))
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        "class": "form-control",
        "placeholder": "you@example.com",
    }))
    message = forms.CharField(widget=forms.Textarea(attrs={
        "class": "form-control",
        "placeholder": "Write your message...",
        "rows": 5,
    }))

    def clean_name(self):
        name = (self.cleaned_data.get("name") or "").strip()
        if len(name) < 2:
            raise forms.ValidationError("Please enter your full name.")
        return name

    def clean_message(self):
        msg = (self.cleaned_data.get("message") or "").strip()
        if len(msg) < 10:
            raise forms.ValidationError("Message must be at least 10 characters.")
        return msg


def _time_choices():
    """30-minute slots from 09:00 to 20:30 (shop closes at 21:00)."""
    start = timezone.datetime.strptime("09:00", "%H:%M").time()
    end = timezone.datetime.strptime("20:30", "%H:%M").time()
    cur = timezone.datetime.combine(timezone.now().date(), start)
    end_dt = timezone.datetime.combine(timezone.now().date(), end)
    out = []
    while cur <= end_dt:
        t = cur.time()
        label = t.strftime("%H:%M")
        out.append((label, label))
        cur += timezone.timedelta(minutes=30)
    return out


class BookingForm(forms.ModelForm):
    service = forms.ModelChoiceField(
        queryset=Service.objects.all(),
        empty_label=_t("Select a service", "Zgjidh një shërbim"),
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    date = forms.DateField(
        widget=forms.DateInput(attrs={"class": "form-control", "type": "date"}),
    )
    time = forms.ChoiceField(
        choices=_time_choices(),
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    class Meta:
        model = Appointment
        fields = ["service", "date", "time", "full_name", "phone", "email", "notes"]
        widgets = {
            "full_name": forms.TextInput(attrs={"class": "form-control", "placeholder": _t("Full name", "Emër & Mbiemër")}),
            "phone": forms.TextInput(attrs={"class": "form-control", "placeholder": _t("Phone number", "Numër telefoni")}),
            "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": _t("Email (optional)", "Email (opsionale)")}),
            "notes": forms.TextInput(attrs={"class": "form-control", "placeholder": _t("Notes (optional)", "Shënim (opsionale)")}),
        }

    def clean_date(self):
        d = self.cleaned_data.get("date")
        if not d:
            return d
        if d < timezone.localdate():
            raise forms.ValidationError(_t("Please choose a future date.", "Ju lutem zgjidhni një datë në të ardhmen."))
        # Monday off
        if d.weekday() == 0:
            raise forms.ValidationError(_t("We are closed on Monday.", "Të hënën jemi pushim."))
        return d

    def clean_time(self):
        val = (self.cleaned_data.get("time") or "").strip()
        try:
            return timezone.datetime.strptime(val, "%H:%M").time()
        except Exception:
            raise forms.ValidationError(_t("Please choose a valid time.", "Ju lutem zgjidhni një orar të vlefshëm."))

    def clean(self):
        cleaned = super().clean()
        d = cleaned.get("date")
        t = cleaned.get("time")
        if d and t:
            # Monday closed.
            if d.weekday() == 0:
                raise forms.ValidationError(_t("Closed on Monday.", "Të hënën jemi mbyllur."))

            dt = timezone.make_aware(timezone.datetime.combine(d, t), timezone.get_current_timezone())
            if dt < timezone.now():
                raise forms.ValidationError(_t("You can’t book a time in the past.", "Nuk mund të rezervoni një orar në të kaluarën."))

            # Conflict check (prevents double booking in normal cases)
            if Appointment.objects.filter(date=d, time=t).exists():
                raise forms.ValidationError(_t(
                    "That time is already booked. Please choose another slot.",
                    "Ky orar është i zënë. Ju lutem zgjidhni një orar tjetër."
                ))
        return cleaned
