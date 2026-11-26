from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator, RegexValidator
from django.db import models
from django.utils import timezone


def validate_past_date(value):
    if value >= timezone.localdate():
        raise ValidationError("La date doit être antérieure à aujourd'hui.")


class User(AbstractUser):
    """Modèle utilisateur personnalisé (point d'extension du projet)."""
    pass


class Specialty(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Doctor(User):
    license_number = models.CharField(
        max_length=6, unique=True, validators=[MinLengthValidator(6)]
    )
    phone = models.CharField(
        max_length=8,
        validators=[RegexValidator(r'^\d{8}$', "Le numéro doit contenir 8 chiffres.")],
    )
    specialties = models.ManyToManyField(Specialty, related_name='doctors', blank=True)

    def __str__(self):
        return f"Dr {self.first_name} {self.last_name}"


class Patient(User):
    national_id = models.CharField(
        max_length=8,
        unique=True,
        validators=[RegexValidator(r'^\d{8}$', "Le CIN doit contenir 8 chiffres.")],
    )
    phone = models.CharField(
        max_length=8,
        validators=[RegexValidator(r'^\d{8}$', "Le numéro doit contenir 8 chiffres.")],
    )
    birth_date = models.DateField(validators=[validate_past_date])

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
