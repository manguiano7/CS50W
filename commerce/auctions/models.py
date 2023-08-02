from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django import forms
from decimal import *

class User(AbstractUser):
    id = models.AutoField(primary_key=True)

class Auction_listings(models.Model):
    id = models.AutoField(primary_key=True)
    Title = models.CharField(max_length=20)
    Description = models.TextField(max_length=1000)
    Starting_bid = models.DecimalField(max_digits=8, decimal_places=2, 
        validators=[
            MaxValueValidator(9999),
            MinValueValidator(Decimal('0.01'))
        ])
    Current_bid = models.DecimalField(blank=True, null=True, max_digits=8, decimal_places=2, 
        validators=[
            MaxValueValidator(9999),
            MinValueValidator(Decimal('0.01'))
        ])

    Image_URL = models.CharField(blank=True, null=True, max_length=2000)
    CATEGORY_CHOICES = (
        (None, 'Category'),
        ('electronics', 'Electronics'),
        ('clothing', 'Clothing'),
        ('home', 'Home and Kitchen'),
        ('beauty', 'Beauty and Personal Care'),
        ('books', 'Books'),
        ('jewelry', 'Jewelry'),
        ('pet_supplies', 'Pet Supplies'),
        ('pets', 'Pets'),
        ('sports_and_outdoors', 'Sports and Outdoors')
    )
    Category = models.CharField(max_length=20,choices=CATEGORY_CHOICES)
    Creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="creator_listings")
    Winner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_winnings", null=True,blank=True,default=None)
    Watchers = models.ManyToManyField(User, null=True, blank=True)
    Is_active = models.BooleanField(default=True)
    def __str__(self):
        return f"{self.Title}"

class Bids(models.Model):
    id = models.AutoField(primary_key=True)
    auction_listing = models.ForeignKey(Auction_listings, on_delete=models.CASCADE, related_name="auction_bids")
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_bids")
    bid_amount = models.DecimalField(max_digits=8, decimal_places=2, 
        validators=[
            MaxValueValidator(9999),
            MinValueValidator(Decimal('0.01'))
        ])

class Comments(models.Model):
    id = models.AutoField(primary_key=True)

    auction_listing = models.ForeignKey(Auction_listings, on_delete=models.CASCADE, related_name="auction_comments")
    commenter = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_comments")
    Comment = models.TextField(max_length=200)

