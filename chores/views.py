from django.shortcuts import get_object_or_404, redirect, render

from .forms import ChoreAssigneeForm, ChoreForm
from .models import Chore


def chore_list(request):
    chores = Chore.objects.order_by("due_date", "due_time", "id")
    return render(request, "chores/chore_list.html", {"chores": chores})


def chore_create(request):
    form = ChoreForm(request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("chores:list")

    return render(request, "chores/chore_form.html", {"form": form})


def chore_assign(request, pk):
    chore = get_object_or_404(Chore, pk=pk)
    form = ChoreAssigneeForm(
        request.POST if request.method == "POST" else None,
        instance=chore,
    )
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("chores:list")

    return render(
        request,
        "chores/chore_assignee_form.html",
        {"chore": chore, "form": form},
    )
