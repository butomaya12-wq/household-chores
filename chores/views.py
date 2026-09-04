from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import ChoreAssigneeForm, ChoreForm
from .models import Chore


def chore_list(request):
    chores = Chore.objects.filter(status=Chore.Status.OPEN).order_by(
        "due_date", "due_time", "id"
    )
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


@require_POST
def chore_complete(request, pk):
    chore = get_object_or_404(Chore, pk=pk)
    chore.status = Chore.Status.COMPLETED
    chore.save(update_fields=["status"])
    return redirect("chores:list")


def chore_completed_list(request):
    chores = Chore.objects.filter(status=Chore.Status.COMPLETED).order_by(
        "due_date", "due_time", "id"
    )
    return render(request, "chores/chore_completed_list.html", {"chores": chores})
