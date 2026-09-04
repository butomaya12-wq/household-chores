from datetime import time, timedelta

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .forms import ChoreAssigneeForm, ChoreForm
from .models import Chore, HouseholdMember


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

    def test_chore_stores_one_assignee(self):
        first_member = HouseholdMember.objects.create(name="Alex")
        second_member = HouseholdMember.objects.create(name="Sam")
        chore = Chore.objects.create(
            title="Wash dishes",
            due_date=timezone.localdate(),
            assignee=first_member,
        )

        chore.assignee = second_member
        chore.save()
        chore.refresh_from_db()

        self.assertEqual(chore.assignee, second_member)

    def test_new_chore_is_open(self):
        chore = Chore.objects.create(
            title="Wash dishes", due_date=timezone.localdate()
        )

        self.assertEqual(chore.status, Chore.Status.OPEN)


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


class ChoreAssigneeFormTests(TestCase):
    def setUp(self):
        self.member = HouseholdMember.objects.create(name="Alex")

    def test_form_accepts_an_existing_household_member(self):
        form = ChoreAssigneeForm(data={"assignee": self.member.pk})

        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["assignee"], self.member)

    def test_form_requires_a_household_member(self):
        form = ChoreAssigneeForm(data={"assignee": ""})

        self.assertFalse(form.is_valid())
        self.assertIn("assignee", form.errors)


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

    def test_assigning_a_member_updates_an_existing_chore(self):
        first_member = HouseholdMember.objects.create(name="Alex")
        second_member = HouseholdMember.objects.create(name="Sam")
        chore = Chore.objects.create(
            title="Wash dishes",
            due_date=timezone.localdate(),
            assignee=first_member,
        )

        response = self.client.post(
            reverse("chores:assign", args=[chore.pk]),
            data={"assignee": second_member.pk},
        )

        self.assertRedirects(response, reverse("chores:list"))
        chore.refresh_from_db()
        self.assertEqual(chore.assignee, second_member)

    def test_assignment_form_displays_existing_household_members(self):
        member = HouseholdMember.objects.create(name="Alex")
        chore = Chore.objects.create(
            title="Wash dishes", due_date=timezone.localdate()
        )

        response = self.client.get(reverse("chores:assign", args=[chore.pk]))

        self.assertContains(response, member.name)

    def test_assignee_is_visible_in_the_chore_list(self):
        member = HouseholdMember.objects.create(name="Alex")
        Chore.objects.create(
            title="Wash dishes",
            due_date=timezone.localdate(),
            assignee=member,
        )

        response = self.client.get(reverse("chores:list"))

        self.assertContains(response, "responsible: Alex")

    def test_post_marks_chore_completed_without_authentication(self):
        member = HouseholdMember.objects.create(name="Alex")
        chore = Chore.objects.create(
            title="Wash dishes",
            due_date=timezone.localdate(),
            assignee=member,
        )

        response = self.client.post(reverse("chores:complete", args=[chore.pk]))

        self.assertRedirects(response, reverse("chores:list"))
        chore.refresh_from_db()
        self.assertEqual(chore.status, Chore.Status.COMPLETED)
        self.assertEqual(chore.assignee, member)

    def test_completed_chore_is_not_in_the_active_list(self):
        active_chore = Chore.objects.create(
            title="Wash dishes", due_date=timezone.localdate()
        )
        completed_chore = Chore.objects.create(
            title="Take out trash",
            due_date=timezone.localdate(),
            status=Chore.Status.COMPLETED,
        )

        response = self.client.get(reverse("chores:list"))

        self.assertContains(response, active_chore.title)
        self.assertNotContains(response, completed_chore.title)

    def test_completed_list_shows_status_assignee_and_due_date(self):
        member = HouseholdMember.objects.create(name="Alex")
        due_date = timezone.localdate()
        chore = Chore.objects.create(
            title="Wash dishes",
            due_date=due_date,
            assignee=member,
            status=Chore.Status.COMPLETED,
        )

        response = self.client.get(reverse("chores:completed_list"))

        self.assertContains(response, chore.title)
        self.assertContains(response, "status: Completed")
        self.assertContains(response, "responsible: Alex")
        self.assertContains(response, due_date.isoformat())

    def test_completion_requires_post(self):
        chore = Chore.objects.create(
            title="Wash dishes", due_date=timezone.localdate()
        )

        response = self.client.get(reverse("chores:complete", args=[chore.pk]))

        self.assertEqual(response.status_code, 405)
        chore.refresh_from_db()
        self.assertEqual(chore.status, Chore.Status.OPEN)

    def test_full_mvp_flow(self):
        member = HouseholdMember.objects.create(name="Alex")
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
        chore = Chore.objects.get(title="Wash dishes")
        self.assertEqual(chore.due_date, due_date)
        self.assertEqual(chore.due_time, time(18, 30))

        response = self.client.post(
            reverse("chores:assign", args=[chore.pk]),
            data={"assignee": member.pk},
        )

        self.assertRedirects(response, reverse("chores:list"))
        chore.refresh_from_db()
        self.assertEqual(chore.assignee, member)

        response = self.client.post(reverse("chores:complete", args=[chore.pk]))

        self.assertRedirects(response, reverse("chores:list"))
        chore.refresh_from_db()
        self.assertEqual(chore.status, Chore.Status.COMPLETED)

        response = self.client.get(reverse("chores:list"))
        self.assertNotContains(response, chore.title)

        response = self.client.get(reverse("chores:completed_list"))
        self.assertContains(response, chore.title)
        self.assertContains(response, "status: Completed")
        self.assertContains(response, "responsible: Alex")
        self.assertContains(response, due_date.isoformat())
