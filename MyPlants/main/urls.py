from django.urls import path
from . import views 

urlpatterns = [
path("", views.index, name="index"),
path("home/", views.home, name="home"),
path("create/", views.create, name="create"),
path("view/", views.view, name="view"),
path("add/", views.add_plant, name="add"),
path("share/", views.share, name="share"),
path("requests/", views.requests, name="requests"),
path("notifications/", views.notifications, name="notifications"),
path("logout/", views.logout_view, name="logout"),
path("out/", views.out, name="out"),
path("profile/", views.profile, name="profile"),
path("delete/", views.delete, name="delete"),
path("delete-account/", views.delete_account, name="delete_account"),
path('delete-plants/', views.delete_plants, name='delete_plants'),
path("<int:id>", views.list, name="list"),
path('share/success/', views.share_success, name='share_success'),
]

