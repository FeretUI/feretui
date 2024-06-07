from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("feretui/static/<filepath>", views.feretui_static_file),
    path("feretui/action/<action>", views.call_action),
]
