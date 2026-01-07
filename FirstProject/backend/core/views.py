from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.utils.translation import get_language
from django.urls import reverse
from django.db import IntegrityError, transaction


def _t(en: str, sq: str) -> str:
    lang = (get_language() or "en").lower()
    return sq if lang.startswith("sq") else en

from .models import Service, ContactMessage
from .forms import ContactForm, BookingForm

BUSINESS = {
    "name": "Redi Hair Studio",
    "city": "Peshkopi",
    "address": 'Rruga “Tercilio Kardinali”, përball Hotel Veri',
    "phone": "+355 68 289 7018",
    "instagram": "redi_hair_studio",
    "hours": "09:00–21:00",
    "off_day_en": "Monday",
    "off_day_sq": "E Hënë",
}

def home(request):
    services = Service.objects.all()
    booking_form = BookingForm()
    return render(request, "home.html", {"services": services, "booking_form": booking_form, "biz": BUSINESS})


@require_http_methods(["POST"])
def book(request):
    form = BookingForm(request.POST)
    if form.is_valid():
        try:
            with transaction.atomic():
                form.save()
        except IntegrityError:
            # Database-level unique constraint caught (handles race conditions)
            form.add_error(None, _t(
                "That time is already booked. Please choose another slot.",
                "Ky orar është i zënë. Ju lutem zgjidhni një orar tjetër."
            ))
            services = Service.objects.all()
            messages.error(request, _t(
                "Please fix the booking form errors.",
                "Ju lutem korrigjoni gabimet në formularin e rezervimit."
            ))
            return render(request, "home.html", {"services": services, "booking_form": form, "biz": BUSINESS})
        messages.success(request, _t(
            "Your booking request was sent successfully.",
            "Rezervimi u dërgua me sukses. Ne do ta konfirmojmë së shpejti."
        ))
        return redirect(f"{reverse('home')}#booking")
    # If invalid, re-render home with errors
    services = Service.objects.all()
    messages.error(request, _t("Please fix the booking form errors.", "Ju lutem korrigjoni gabimet në formularin e rezervimit."))
    return render(request, "home.html", {"services": services, "booking_form": form, "biz": BUSINESS})

def about(request):
    return render(request, "about.html", {"biz": BUSINESS})

@require_http_methods(["GET", "POST"])
def contact(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            ContactMessage.objects.create(
                name=form.cleaned_data["name"],
                email=form.cleaned_data["email"],
                message=form.cleaned_data["message"],
            )
            messages.success(request, _t("Thanks! Your message has been sent.", "Faleminderit! Mesazhi u dërgua me sukses."))
            return redirect("contact")
        messages.error(request, _t("Please fix the errors below.", "Ju lutem korrigjoni gabimet më poshtë."))
    else:
        form = ContactForm()
    return render(request, "contact.html", {"form": form, "biz": BUSINESS})
