from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class Chore(models.Model):
    title = models.CharField(max_length=200)
    due_date = models.DateField()
    due_time = models.TimeField(blank=True, null=True)

    def clean(self):
        super().clean()
        if self.due_date and self.due_date < timezone.localdate():
            raise ValidationError(
                {"due_date": "Due date cannot be in the past."}
            )
