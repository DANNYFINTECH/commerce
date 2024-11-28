from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),  # Index page
    path("login/", views.login_view, name="login"),  # Login page
    path("logout/", views.logout_view, name="logout"),  # Logout page
    path("register/", views.register, name="register"),  # Register page
    path("create_listing/", views.create_listing, name="create_listing"),  # Create listing page
    path("listing/<int:listing_id>/", views.listing_detail, name="listing_detail"),  # Listing detail page
    path("watchlist/", views.watchlist_view, name="watchlist"),  # Watchlist page for logged in users
    path("categories/", views.categories, name="categories"),  # Categories overview page
    path("categories/<int:category_id>/", views.category_listings, name="category_listings"),  # Listings filtered by category
]
