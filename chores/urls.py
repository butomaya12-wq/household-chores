from django.urls import path

from . import views

app_name = "chores"

urlpatterns = [
    path("", views.chore_list, name="list"),
    path("new/", views.chore_create, name="create"),
    path("<int:pk>/assign/", views.chore_assign, name="assign"),
]
