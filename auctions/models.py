from email.policy import default
from tkinter import CASCADE
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from datetime import datetime

class User(AbstractUser):
    pass

class Auction(models.Model):
    title = models.CharField(max_length=64)
    description = models.CharField(max_length=240)
    image = models.URLField()
    category = models.CharField(max_length=16)
    start = models.IntegerField()
    last_bid = models.IntegerField(default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    running = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.user} - {self.title}"

class Watchlist(models.Model):
    product = models.ForeignKey(Auction, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    watching = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user} - {self.product} - Watching: {self.watching}"

class Bid(models.Model):
    product = models.ForeignKey(Auction, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    bid = models.IntegerField()

    def __str__(self):
        return f"{self.product} - {self.user} - ${self.bid}"

class Comment(models.Model):
    product = models.ForeignKey(Auction, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.CharField(max_length=240)
    time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product} - {self.user} - ${self.comment}"