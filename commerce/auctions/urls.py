from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("listing_page/<int:listing_id>/", views.listing_page, name="listing_page"),
    path("listing_page/<int:listing_id>/<str:is_bid_error>", views.listing_page, name="listing_page_bet"),
    path("create_listing", views.create_listing, name="create_listing"),
    path("place_bid/<int:listing_id>", views.place_bid, name="place_bid"),
    path("get_watchlist/", views.get_watchlist, name="get_watchlist"),
    path("add_to_watchlist/<int:listing_id>", views.add_to_watchlist, name="add_to_watchlist"),
    path("remove_from_watchlist/<int:listing_id>", views.remove_from_watchlist, name="remove_from_watchlist"),
    path("close_auction/<int:listing_id>", views.close_auction, name="close_auction"),
    path("add_comment/<int:listing_id>", views.add_comment, name="add_comment"),
    path("categories/", views.categories, name="categories"),
    path("categories/<str:category>", views.categories, name="category"),
]