
from asyncio.windows_events import NULL
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .models import User, Auction, Watchlist, Bid, Comment



def index(request):
    categories = Auction.objects.values_list('category', flat=True).order_by('category').distinct()
    return render(request, "auctions/index.html", {
        "listings": Auction.objects.all(),
        "categories": categories
    })

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

@login_required(login_url='login')
def create(request):
    if request.method == "GET":
        return render(request, "auctions/create.html")
    else:
        title = request.POST["title"]
        category = request.POST["category"]
        description = request.POST["description"]
        image = request.POST["image"]
        start = request.POST["start"]
        listing = Auction(title=title, category=category, description=description, image=image, start=start, user=request.user)
        listing.save()
        return HttpResponseRedirect(reverse("index"))

@login_required(login_url='login')
def listing(request, listing):
    user = request.user

    # Queries
    product_id = Auction.objects.get(title=listing).id
    auction = Auction.objects.get(title=listing, id=product_id)
    Watchlist.objects.get_or_create(product_id=product_id, user=user)
    watchlist = Watchlist.objects.filter(product_id=product_id, user=user).values()
    bids = Bid.objects.filter(product=product_id).count()
    last_bidder = NULL
    comments = Comment.objects.filter(product=product_id).order_by('time').reverse
    categories = Auction.objects.values_list('category', flat=True).order_by('category').distinct()
    start = Auction.objects.get(title=listing).start
    last_bid = Auction.objects.get(id=product_id).last_bid
    bid = 0
    attempt_success = NULL
    
    if bids > 0:
        last_bidder = User.objects.get(username=Bid.objects.get(bid=auction.last_bid).user)

    # Load page from Active Listings
    if request.method == "GET":
        return render(request, "auctions/listing.html", {
            "listing": auction,
            "watching": watchlist[0]['watching'], #Bool for watchlist
            "user": user,
            "bids": bids,
            "last_bidder": last_bidder,
            "comments": comments,
            "categories": categories,
            "attempt_success": attempt_success
        })
    elif request.method == "POST":
        # Watchlist Button
        if request.POST['watching']:
            if request.POST['watching'] == "add":
                Watchlist.objects.filter(product_id=product_id, user=request.user).update(watching=True)
            elif request.POST['watching'] == "rm":
                Watchlist.objects.filter(product_id=product_id, user=request.user).update(watching=False)
            elif request.POST['watching'] == "bid":
                if last_bid == 0:
                    last_bid = start
                bid = int(request.POST['bid'])
            
                if bid > last_bid:
                    Bid.objects.get_or_create(product_id=product_id, user=user, bid=bid)
                    Auction.objects.filter(id=product_id, title=listing).update(last_bid=bid)
                    attempt_success = True
                else:
                    attempt_success = False
    return HttpResponseRedirect(reverse("listing", kwargs={'listing':listing}))

@login_required(login_url='login')
def watchlist(request):
    categories = Auction.objects.values_list('category', flat=True).order_by('category').distinct()
    user = request.user
    watchlist= []
    for item in Watchlist.objects.filter(user=user, watching=True).values():
        watchlist.append(Auction.objects.get(id=item['product_id']))
    return render(request, "auctions/watchlist.html", {
        "listings": watchlist,
        "categories": categories
    })

@login_required(login_url='login')
def close(request, listing):
    product_id = Auction.objects.get(title=listing).id
    Auction.objects.filter(id=product_id).update(running=False)
    Watchlist.objects.filter(id=product_id).delete()
    return HttpResponseRedirect(reverse("listing", kwargs={'listing':listing}))

def comment(request,listing):
    product = Auction.objects.get(title=listing)
    user = request.user
    comment = request.POST['comment']
    Comment.objects.get_or_create(product=product, user=user, comment=comment)
    return HttpResponseRedirect(reverse("listing", kwargs={'listing':listing}))

def category(request, category):
    listings = Auction.objects.filter(category=category).values()
    categories = Auction.objects.values_list('category', flat=True).order_by('category').distinct()
    return render (request, "auctions/categories.html", {
        "category": category,
        "categories": categories,
        "listings": listings
    })