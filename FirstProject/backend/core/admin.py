from django.contrib import admin
from .models import Service, ContactMessage, Appointment

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("id", "name_en", "name_sq", "price")
    search_fields = ("name_en", "name_sq")
    list_editable = ("price",)

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "email", "created_at")
    search_fields = ("name", "email", "message")
    readonly_fields = ("created_at",)


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ("id", "full_name", "phone", "service", "date", "time", "created_at")
    list_filter = ("date", "service")
    search_fields = ("full_name", "phone", "email", "notes")
    readonly_fields = ("created_at",)
