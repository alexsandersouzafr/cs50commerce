from django.contrib import admin

from .models import User, Auction, Watchlist, Bid, Comment
# Register your models here.

admin.site.register(Auction)
admin.site.register(User)
admin.site.register(Watchlist)
admin.site.register(Bid)
admin.site.register(Comment)