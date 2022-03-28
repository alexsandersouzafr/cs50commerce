from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create, name="create"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("category/<str:category>", views.category, name="category"),
    path("<str:listing>", views.listing, name="listing"),
    path("<str:listing>/bid", views.listing, name="bid"),
    path("<str:listing>/close", views.close, name="close"),
    path("<str:listing>/comment", views.comment, name="comment")
]
