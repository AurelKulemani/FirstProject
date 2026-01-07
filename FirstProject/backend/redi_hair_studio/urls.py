from django.contrib import admin
from django.urls import path, include
from core import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('i18n/', include('django.conf.urls.i18n')),
    path('', views.home, name='home'),
    path('book/', views.book, name='book'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
]
