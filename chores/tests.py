from datetime import time, timedelta

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .forms import ChoreForm
from .models import Chore


class ChoreModelTests(TestCase):
    def test_chore_with_today_due_date_is_valid(self):
        chore = Chore(title="Wash dishes", due_date=timezone.localdate())

        chore.full_clean()

    def test_chore_with_past_due_date_is_invalid(self):
        chore = Chore(
            title="Wash dishes",
            due_date=timezone.localdate() - timedelta(days=1),
        )

        with self.assertRaises(ValidationError) as error:
            chore.full_clean()

        self.assertIn("due_date", error.exception.message_dict)


class ChoreFormTests(TestCase):
    def test_form_accepts_a_future_due_date_and_optional_due_time(self):
        form = ChoreForm(
            data={
                "title": "Wash dishes",
                "due_date": timezone.localdate() + timedelta(days=1),
                "due_time": "18:30",
            }
        )

        self.assertTrue(form.is_valid())

    def test_form_rejects_a_blank_title(self):
        form = ChoreForm(
            data={"title": "", "due_date": timezone.localdate(), "due_time": ""}
        )

        self.assertFalse(form.is_valid())
        self.assertIn("title", form.errors)

    def test_form_rejects_a_missing_due_date(self):
        form = ChoreForm(data={"title": "Wash dishes", "due_date": "", "due_time": ""})

        self.assertFalse(form.is_valid())
        self.assertIn("due_date", form.errors)

    def test_form_rejects_a_past_due_date(self):
        form = ChoreForm(
            data={
                "title": "Wash dishes",
                "due_date": timezone.localdate() - timedelta(days=1),
                "due_time": "",
            }
        )

        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["due_date"], ["Due date cannot be in the past."])


class ChoreViewsTests(TestCase):
    def test_successful_post_creates_chore_and_shows_it_in_the_list(self):
        due_date = timezone.localdate() + timedelta(days=1)

        response = self.client.post(
            reverse("chores:create"),
            data={
                "title": "Wash dishes",
                "due_date": due_date,
                "due_time": "18:30",
            },
        )

        self.assertRedirects(response, reverse("chores:list"))
        chore = Chore.objects.get()
        self.assertEqual(chore.title, "Wash dishes")
        self.assertEqual(chore.due_date, due_date)
        self.assertEqual(chore.due_time, time(18, 30))

        response = self.client.get(reverse("chores:list"))

        self.assertContains(response, "Wash dishes")
        self.assertContains(response, due_date.isoformat())

    def test_invalid_post_returns_form_errors_without_creating_a_chore(self):
        response = self.client.post(
            reverse("chores:create"),
            data={"title": "", "due_date": "", "due_time": ""},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Chore.objects.count(), 0)
        self.assertFormError(response.context["form"], "title", "This field is required.")
        self.assertFormError(response.context["form"], "due_date", "This field is required.")

    def test_empty_post_returns_required_field_errors(self):
        response = self.client.post(reverse("chores:create"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Chore.objects.count(), 0)
        self.assertFormError(response.context["form"], "title", "This field is required.")
        self.assertFormError(response.context["form"], "due_date", "This field is required.")
