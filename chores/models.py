from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class HouseholdMember(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Chore(models.Model):
    class Status(models.TextChoices):
        OPEN = "open", "Open"
        COMPLETED = "completed", "Completed"

    title = models.CharField(max_length=200)
    due_date = models.DateField()
    due_time = models.TimeField(blank=True, null=True)
    assignee = models.ForeignKey(
        HouseholdMember,
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name="chores",
    )
    status = models.CharField(
        choices=Status.choices,
        default=Status.OPEN,
        max_length=10,
    )

    def clean(self):
        super().clean()
        if self.due_date and self.due_date < timezone.localdate():
            raise ValidationError(
                {"due_date": "Due date cannot be in the past."}
            )
