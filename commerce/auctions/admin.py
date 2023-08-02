from django.contrib import admin
from .models import User, Auction_listings, Bids, Comments

# Register your models here.

class AuctionAdmin(admin.ModelAdmin):
    list_display = ("Title", "Starting_bid", "Current_bid", "Category", "Creator",  )

class BidsAdmin(admin.ModelAdmin):
    list_display = ("auction_listing", "bidder", "bid_amount")

class CommentsAdmin(admin.ModelAdmin):
    list_display = ("auction_listing", "commenter")

#I can manage anything here from admin
#uses flightadmin settings
admin.site.register(Auction_listings, AuctionAdmin)

admin.site.register(Bids, BidsAdmin)
admin.site.register(Comments ,CommentsAdmin)

#admin.site.register(Passenger, PassengerAdmin)