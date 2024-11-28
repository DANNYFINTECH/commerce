from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import User, Listing, Category, Bid, Watchlist, Comment
from .forms import ListingForm, BidForm  # Ensure BidForm is imported

# Index View - Show active and closed listings
def index(request):
    active_listings = Listing.objects.filter(is_active=True)
    closed_listings = Listing.objects.filter(is_active=False)

    return render(request, "auctions/index.html", {
        "active_listings": active_listings,
        "closed_listings": closed_listings,
        "watchlist_url": reverse("watchlist") if request.user.is_authenticated else None  # Watchlist link for logged-in users
    })

# Login View
def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")

# Logout View
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))

# Register View
def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

# Create Listing View
@login_required
def create_listing(request):
    if request.method == "POST":
        form = ListingForm(request.POST, request.FILES)  # Support file uploads
        if form.is_valid():
            listing = form.save(commit=False)
            listing.creator = request.user  # Set the creator of the listing
            listing.save()  # Save the listing
            return HttpResponseRedirect(reverse("index"))
    else:
        form = ListingForm()

    categories = Category.objects.all()
    return render(request, "auctions/create_listing.html", {
        'form': form,
        'categories': categories  # Pass categories to the template for the dropdown
    })

# Listing Detail View
def listing_detail(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)
    bids = Bid.objects.filter(listing=listing).order_by('-timestamp')  # Get all bids for this listing, ordered by date
    comments = Comment.objects.filter(listing=listing).order_by('-timestamp')  # Get all comments for this listing
    is_watching = Watchlist.objects.filter(user=request.user, listing=listing).exists() if request.user.is_authenticated else False

    # Get the highest bid for a closed auction
    highest_bid = bids.first() if bids else None
    has_won = False

    if listing.is_active == False and highest_bid and request.user.is_authenticated and highest_bid.user == request.user:
        has_won = True  # The signed-in user is the highest bidder and won the auction

    # Handle different POST actions
    if request.method == "POST":
        # Close auction
        if 'close_auction' in request.POST and request.user == listing.creator:
            listing.is_active = False
            listing.save()
            return HttpResponseRedirect(reverse("listing_detail", args=[listing_id]))

        # Place a bid
        elif 'place_bid' in request.POST:
            bid_form = BidForm(request.POST)
            if bid_form.is_valid():
                bid_amount = bid_form.cleaned_data["bid_amount"]
                if highest_bid and bid_amount <= highest_bid.amount:
                    # Show an error message if the bid is not higher than the current highest bid
                    messages.error(request, "Your bid needs to be higher than the current highest bid.")
                    return render(request, "auctions/listing_detail.html", {
                        "listing": listing,
                        "bids": bids,
                        "comments": comments,
                        "is_watching": is_watching,
                        "bid_form": BidForm(),
                        "error_message": "Your bid needs to be higher than the current highest bid.",
                        "has_won": has_won
                    })
                else:
                    # Create the new bid and update the listing
                    Bid.objects.create(listing=listing, user=request.user, amount=bid_amount)
                    listing.current_price = bid_amount
                    listing.save()
                    return HttpResponseRedirect(reverse("listing_detail", args=[listing_id]))

        # Toggle watchlist
        elif 'toggle_watchlist' in request.POST:
            if is_watching:
                Watchlist.objects.filter(user=request.user, listing=listing).delete()  # Remove from watchlist
            else:
                Watchlist.objects.create(user=request.user, listing=listing)  # Add to watchlist
            return HttpResponseRedirect(reverse("listing_detail", args=[listing_id]))  # Redirect to the same page to reflect changes

        # Add comment
        elif 'add_comment' in request.POST:
            comment_content = request.POST["comment_content"]
            Comment.objects.create(listing=listing, user=request.user, content=comment_content)
            return HttpResponseRedirect(reverse("listing_detail", args=[listing_id]))

    return render(request, "auctions/listing_detail.html", {
        "listing": listing,
        "bids": bids,
        "comments": comments,
        "is_watching": is_watching,
        "bid_form": BidForm(),
        "has_won": has_won  # Pass the information to the template
    })

# Watchlist View - Display all listings the user is watching
@login_required
def watchlist_view(request):
    # Fetch all listings the user has added to their watchlist
    watchlist_items = Watchlist.objects.filter(user=request.user)  
    listings = [item.listing for item in watchlist_items]  # Extract the listings from the watchlist
    return render(request, "auctions/watchlist.html", {
        "listings": listings  # Pass the listings to the template
    })

# Category List View - Display all categories
def categories(request):
    categories = Category.objects.all()  # Fetch all categories
    return render(request, "auctions/categories.html", {
        "categories": categories  # Pass the categories to the template
    })

# Listings by Category View (Ensure this function is present)
def category_listings(request, category_id):
    category = get_object_or_404(Category, pk=category_id)  # Get the category by ID
    listings = Listing.objects.filter(category=category, is_active=True)  # Fetch active listings in this category
    return render(request, "auctions/category_listings.html", {
        "category": category,
        "listings": listings
    })
