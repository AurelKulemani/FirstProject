from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import get_language

class Service(models.Model):
    name_en = models.CharField(max_length=120)
    name_sq = models.CharField(max_length=120)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        ordering = ["id"]

    @property
    def display_name(self) -> str:
        lang = (get_language() or "en").lower()
        if lang.startswith("sq"):
            return self.name_sq
        return self.name_en

    def __str__(self):
        return f"{self.name_en} - {self.price}"

class ContactMessage(models.Model):
    name = models.CharField(max_length=120)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.email})"


class Appointment(models.Model):
    """A simple booking slot (no duration)."""

    service = models.ForeignKey(Service, on_delete=models.PROTECT, related_name="appointments")
    full_name = models.CharField(max_length=120)
    phone = models.CharField(max_length=40)
    email = models.EmailField(blank=True)
    notes = models.CharField(max_length=255, blank=True)
    date = models.DateField()
    time = models.TimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "-time"]
        constraints = [
            models.UniqueConstraint(fields=["date", "time"], name="unique_booking_slot"),
        ]

    def clean(self):
        # During form validation, Django may call model.clean even if the form has errors.
        # Guard against missing values to avoid TypeError (e.g., date/time not provided).
        if not self.date or not self.time:
            return

        # Prevent booking in the past.
        dt = timezone.make_aware(
            timezone.datetime.combine(self.date, self.time),
            timezone.get_current_timezone(),
        )
        if dt < timezone.now():
            raise ValidationError("You can’t book a time in the past.")

        # Monday closed.
        if self.date.weekday() == 0:
            raise ValidationError("Closed on Monday.")

        # Working hours: 09:00–21:00 (inclusive end). We treat 21:00 as last allowed start.
        if not (timezone.datetime.strptime("09:00", "%H:%M").time() <= self.time <= timezone.datetime.strptime("21:00", "%H:%M").time()):
            raise ValidationError("Please choose a time between 09:00 and 21:00.")

    def __str__(self):
        return f"{self.full_name} • {self.date} {self.time} • {self.service.name_en}"
