from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils import timezone


class Appointment(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'En attente'
        CONFIRMED = 'CONFIRMED', 'Confirmé'
        CANCELLED = 'CANCELLED', 'Annulé'

    reason = models.TextField()
    prescription = models.FileField(
        upload_to='prescriptions/',
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])],
    )
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.PENDING
    )
    duration_minutes = models.PositiveIntegerField(default=30)
    appointment_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    doctor = models.ForeignKey(
        'AccountApp.Doctor', on_delete=models.CASCADE, related_name='appointments'
    )
    patient = models.ForeignKey(
        'AccountApp.Patient', on_delete=models.CASCADE, related_name='appointments'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._original_date = self.appointment_date

    def clean(self):
        # La règle ne s'applique qu'à la création ou si la date est modifiée :
        # un rendez-vous passé reste modifiable (ex. ajout de l'ordonnance).
        if self.appointment_date and (
            self._state.adding or self.appointment_date != self._original_date
        ):
            if self.appointment_date <= timezone.now():
                raise ValidationError(
                    {'appointment_date': "La date doit être postérieure à maintenant."}
                )

    class Meta:
        ordering = ['appointment_date']
        constraints = [
            models.UniqueConstraint(
                fields=['doctor', 'appointment_date'],
                name='unique_doctor_appointment_date',
            )
        ]

    def __str__(self):
        return f"{self.patient} - {self.doctor} ({self.appointment_date:%d/%m/%Y %H:%M})"
