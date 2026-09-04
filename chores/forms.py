from django import forms

from .models import Chore, HouseholdMember


class ChoreForm(forms.ModelForm):
    class Meta:
        model = Chore
        fields = ["title", "due_date", "due_time"]
        widgets = {
            "due_date": forms.DateInput(attrs={"type": "date"}),
            "due_time": forms.TimeInput(attrs={"type": "time"}),
        }


class ChoreAssigneeForm(forms.ModelForm):
    assignee = forms.ModelChoiceField(
        queryset=HouseholdMember.objects.order_by("name"),
        empty_label="Select a household member",
    )

    class Meta:
        model = Chore
        fields = ["assignee"]
