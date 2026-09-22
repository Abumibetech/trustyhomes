from django.urls import path

from . import views

app_name = "agents"

urlpatterns = [
    path("dashboard/", views.dashboard, name="dashboard"),
    path("dashboard/upgrade/", views.upgrade_plan, name="upgrade_plan"),
    path("dashboard/add/", views.add_property, name="add_property"),
    path("dashboard/<int:pk>/edit/", views.edit_property, name="edit_property"),
    path("dashboard/<int:pk>/delete/", views.delete_property, name="delete_property"),
    path("dashboard/<int:pk>/toggle/", views.toggle_availability, name="toggle_availability"),
    path("profile/<int:pk>/", views.public_profile, name="public_profile"),
]
