from django.urls import path

from . import views

app_name = "listings"

urlpatterns = [
    path("", views.property_list, name="property_list"),
    path("favourites/", views.my_favourites, name="my_favourites"),
    path("ajax/area-suggestions/", views.load_area_suggestions, name="load_area_suggestions"),
    path("ajax/property-type-suggestions/", views.load_property_type_suggestions, name="load_property_type_suggestions"),
    path("ads/<int:ad_id>/click/", views.ad_click, name="ad_click"),
    path("agent/<int:agent_id>/review/", views.add_review, name="add_review"),
    path("<slug:slug>/", views.property_detail, name="property_detail"),
    path("<slug:slug>/inspect/", views.request_inspection, name="request_inspection"),
    path("<slug:slug>/report/", views.report_listing, name="report_listing"),
    path("<slug:slug>/favourite/", views.toggle_favourite, name="toggle_favourite"),
    path("<slug:slug>/comment/", views.add_comment, name="add_comment"),
    path("comment/<int:comment_id>/like/", views.toggle_comment_like, name="toggle_comment_like"),
]
