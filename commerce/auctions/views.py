from django.shortcuts import render

# Create your views here.
#todo
#make image url optional
#needs place bid with login required wrapper, because cannot add place_bid functions inside listing_page, because
#login_required needs to be a wrapper
#need to change model for listings, each should have starting_bid AND current_bid
#need to make listing page cleaner
#bids will have history of all bids, but each listing will also have the current bid for

from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.forms import ModelForm
from django.contrib.auth.decorators import login_required
from .models import User, Auction_listings, Bids, Comments

class New_listing(ModelForm):
    class Meta:
        model = Auction_listings
        #fields for form don't include the "current_bid" field, since this is updated after the 
        #listing is created, and after a person makes a bid on the item
        fields = ['Title', 'Description', 'Starting_bid', 'Image_URL', 'Category']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set placeholders equal to field names
        for field_name in self.fields:
            self.fields[field_name].widget.attrs['placeholder'] = field_name.replace('_',' ')
            self.fields[field_name].label = False

class New_Bid(ModelForm):
    class Meta:
        model = Bids
        exclude = ('auction_listing','bidder')

class New_Comment(ModelForm):
    class Meta:
        model = Comments
        exclude = ('auction_listing','commenter')
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set placeholders equal to field names
        for field_name in self.fields:
            self.fields[field_name].widget.attrs['placeholder'] = field_name.replace('_',' ')
            self.fields[field_name].label = False

def index(request):
    #returns all active listings
    auction_listings = Auction_listings.objects.filter(Is_active=True)

    return render(request, "auctions/index.html", {
        "auction_listings": auction_listings,
    })

def categories(request, category=None):
    #if category, filters based on category
    if category != None:
        auction_listings = Auction_listings.objects.filter(Category=category, Is_active=True)
        #if list is NOT empty, there is at least one item with that category
        if auction_listings:
            #displays the first found category
            category = auction_listings[0].get_Category_display()
        else:
            #creates a new (dummy) instance of an auction
            auction_listing = Auction_listings(Category=category)
            category = auction_listing.get_Category_display()

        return render(request, "auctions/category_listings.html", {
            "auction_listings": auction_listings,
            "category": category,
        })

    #provides the different categories to select from
    categories = Auction_listings._meta.get_field('Category').choices

    return render(request, "auctions/categories.html", {
        #omits the first None entry, "Category", which is not selectable
        "categories": categories[1:],
    })

def listing_page(request, listing_id, is_bid_error=None):

    auction_listing = Auction_listings.objects.get(pk=listing_id)
    comments = Comments.objects.filter(auction_listing=auction_listing)

    if request.user.is_authenticated:
        #checks if item is in user's watchlist
        is_in_watchlist =  auction_listing.Watchers.filter(pk=request.user.pk).exists()

        #checks if user created the auction listing
        if (request.user == auction_listing.Creator):
            is_user_creator = True
        else:
            is_user_creator = False

        #checks if user won the auction
        if (request.user == auction_listing.Winner):
            is_user_winner = True
        else:
            is_user_winner = False

    else:
        is_in_watchlist = False
        is_user_winner = False
        is_user_creator = False
   

    return render(request, "auctions/listing_page.html", {
        "auction_listing": auction_listing,
        "bid": New_Bid(),
       
        "comment": New_Comment(),
        #indicates if bid was placed, insuf_bid or success or nothing
        "is_bid_error": is_bid_error,
        "is_in_watchlist": is_in_watchlist,
        "is_logged_in": request.user.is_authenticated,
        "is_user_creator": is_user_creator,
        #checks if auction is still active
        "is_active": auction_listing.Is_active,
        "is_user_winner": is_user_winner,
        "comments": comments,
    })

def create_listing(request):
    if request.method == "POST":
        
        auction_listing = New_listing(request.POST)

        saved_auction = auction_listing.save(commit=False)
        saved_auction.Creator = request.user
        saved_auction.Is_active=True
        #creates an auction record 
        saved_auction.save()

        return HttpResponseRedirect(reverse("index"))
    #else if request method is GET
    return render(request, "auctions/create_listing.html", {
        "auction_listing": New_listing(),
    })

@login_required(login_url = 'login')
def add_to_watchlist(request, listing_id):
    if request.method == "POST":
        auction_listing =  Auction_listings.objects.get(pk=listing_id)

        #only saves if item does not exist in watchlist already
        if not auction_listing.Watchers.filter(pk=request.user.pk).exists():
            auction_listing.Watchers.add(request.user)

    return HttpResponseRedirect(reverse("listing_page",kwargs={'listing_id': listing_id}))

@login_required(login_url = 'login')
def remove_from_watchlist(request, listing_id):
    if request.method == "POST":
        auction_listing = Auction_listings.objects.get(pk=listing_id)
        watchers = auction_listing.Watchers.filter(pk=request.user.pk)
        for watcher in watchers:
            auction_listing.Watchers.remove(watcher)
    return HttpResponseRedirect(reverse("listing_page",kwargs={'listing_id': listing_id}))

@login_required(login_url = 'login')
def get_watchlist(request):
    #items = Watchlist.objects.filter(watcher=request.user)
    auction_listings = Auction_listings.objects.filter(Watchers=request.user)

    return render(request, "auctions/get_watchlist.html", {
        "auction_listings": auction_listings,
    })

@login_required(login_url = 'login')
def close_auction(request, listing_id):
    try:
        auction_listing = Auction_listings.objects.get(pk=listing_id)

        #gets the status id using the related name, first() obtains the first record

        if (auction_listing.Is_active == True and request.user == auction_listing.Creator):
         
            auction_listing.Is_active = False
            
            #updates the winner of the auction listing, if there was a previous bid made
            #if no previous bid was made, current bid is None
            if auction_listing.Current_bid:
                auction_listing.Winner = Bids.objects.filter(auction_listing=auction_listing).order_by('-bid_amount').first().bidder 
        
            auction_listing.save()
        return HttpResponseRedirect(reverse("listing_page",kwargs={'listing_id': listing_id}))
    except Auction_listings.DoesNotExist:
        return HttpResponseRedirect(reverse("index"))

    return HttpResponseRedirect(reverse("index"))

@login_required(login_url = 'login')
def add_comment(request, listing_id):
    comment = New_Comment(request.POST)
    comment = comment.save(commit=False)
    comment.auction_listing = Auction_listings.objects.get(pk=listing_id)
    comment.commenter = request.user
    comment.save()

    return HttpResponseRedirect(reverse("listing_page",kwargs={'listing_id': listing_id}))

@login_required(login_url = 'login')
def place_bid(request, listing_id):

    #defaults to insufficient bid amount
    is_bid_error = "insufficient_bid"

    #POSE request means they placed bid
    if request.method == "POST":
        new_bid = New_Bid(request.POST)
        saved_bid = new_bid.save(commit=False)

        auction_listing = Auction_listings.objects.get(pk=listing_id)

        saved_bid.bidder = request.user
        saved_bid.auction_listing = auction_listing

        #needs to be its own separate auction listing object
        saved_auction =  Auction_listings.objects.get(pk=listing_id)
        saved_auction.Current_bid = saved_bid.bid_amount

        #checks if bid is bigger than starting bid
        if saved_bid.bid_amount >= auction_listing.Starting_bid:

            #checks if any bids were placed previously
            if auction_listing.Current_bid: 

                if saved_bid.bid_amount > auction_listing.Current_bid:
                    saved_bid.save()
                    saved_auction.save()
                    is_bid_error = "success" # "Bid placed!"
             
            else:
                saved_bid.save()
                saved_auction.save()
                #bid placed
                is_bid_error = "success" 
    #listing page BET since a bet was placed
    return HttpResponseRedirect(reverse("listing_page_bet",kwargs={'listing_id': listing_id, 'is_bid_error':is_bid_error}))
 
def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))

def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
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