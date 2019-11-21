from django.shortcuts import render
from .models import Item, UserProfile, Bid
from django.http import JsonResponse
from django.core import serializers
from django.forms.models import model_to_dict
import json
from django.http import QueryDict
import datetime
from django.shortcuts import redirect

def index(request):
    return render(request, 'auction/index.html')

def loginRequired(view):
    def checkRequestLogin(request):
        if 'username' in request.session:
            return view(request)
        else:
            return redirect('/auction/login')
    return checkRequestLogin

def register(request):
    if request.method == 'GET':
        return render(request, 'auction/register.html')
    if request.method == 'POST':
        try:
            username = request.POST.get('username')
            password = request.POST.get('password')
            email = request.POST.get('email')
            dob = request.POST.get('dob')
            user = UserProfile(username = username,password = password,email = email,dob = dob)
            user.save()
            return JsonResponse({'success': 'Register succsesful'})
        except:
            return JsonResponse({'error': 'Username already in use'})

def login(request):
    if request.method == 'GET':
        return render(request, 'auction/login.html')
    elif request.method == 'POST':
        try:
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = UserProfile.objects.get(username = username)
            if password == user.password:
                request.session['username'] = username
                return JsonResponse({'success': 'Login successful'})
            else:
                return JsonResponse({'error': 'Invalid username or password'})
        except UserProfile.DoesNotExist:
            return JsonResponse({'error': 'Invalid username or password'})

def logout(request):
    request.session.flush()
    return redirect('/auction/login')

def listings(request):
    if request.method == 'POST':
        user = UserProfile.objects.get(username=request.session['username'])
        title = request.POST.get('title')
        description = request.POST.get('description')
        image = request.FILES.get('image')
        dateTime = request.POST.get('datetime')
        price = request.POST.get('price')
        item = Item(title=title, description=description, image=image, endDateTime=dateTime, userProfile=user, price=price)
        item.save()
        return JsonResponse({'itemId': item.id})
    elif request.method == 'GET':
        items = Item.objects.filter(endDateTime__gt=datetime.datetime.now())
        context = {
            'items': items
        }
        return render(request, 'auction/listings.html', context)

def listing(request, itemid):
    item = Item.objects.get(pk=itemid)
    expired = item.endDateTime.replace(tzinfo=None) < datetime.datetime.now()
    context = {
        'item': item,
        'expired': expired,
    }
    if expired == True:
        try:
            winningBid = Bid.objects.filter(item=item).latest('amount')
            winner = UserProfile.objects.get(pk=winningBid.userProfile)
            context['winner'] = winner
        except:
            return render(request, 'auction/listing.html', context)
    return render(request, 'auction/listing.html', context)

@loginRequired
def listBid(request):
    return render(request, 'auction/list.html')

# change listings/itemid to use ajax request to refresh page - DONE
# update layout to use bootstrap
# if the listing is finished , top bid can buy
# can no longer bid on item if listing finished
# if listing finished item state updated

def bid(request, itemid):
    if request.method == 'GET':
        item = Item.objects.get(id=itemid)
        relevantBids = Bid.objects.filter(item=item)
        data = []
        for bid in relevantBids:
            user = UserProfile.objects.get(pk=bid.userProfile)
            biddata = {
                'amount': bid.amount,
                'username': user.username
            }
            data.append(biddata)
        return JsonResponse(data, safe=False)

@loginRequired
def bids(request):
    if request.method == 'POST':
        item = Item.objects.get(id=request.POST.get('itemId'))
        # CHECK IF ITEM EXPIRED
        if item.endDateTime < datetime.datetime.now():
            return JsonResponse({'error': 'This item has expired'})
        user = UserProfile.objects.get(username=request.session['username'])
        amount = request.POST.get('amount')
        try:
            relevantBids = Bid.objects.filter(item=item)
            highestBid = relevantBids.latest('amount')
            if highestBid.amount >= float(amount):
                return JsonResponse({'error': 'Bid is too low'})
            item.price = amount
            bid = Bid(userProfile=user, item=item, amount=amount,bidDateTime=datetime.datetime.now())
            bid.save()
            item.save()
            return JsonResponse({'success': 'successfully created bid'})
        except:
            firstBid = Bid(userProfile=user, item=item, amount=amount,bidDateTime=datetime.datetime.now())
            firstBid.save()
            item.price = amount
            item.save()
            return JsonResponse({'success': 'successfully created bid'})

@loginRequired
def profile(request):
    user = UserProfile.objects.get(username=request.session['username'])
    bids = Bid.objects.filter(userProfile=user)
    openBids = []
    winningBids = []
    lostBids = []
    for bid in bids:
        item = Item.objects.get(pk=bid.item.pk)
        if item.endDateTime.replace(tzinfo=None) < datetime.datetime.now():
            itemBids = Bid.objects.filter(item=item)
            if itemBids.latest('amount') == bid:
                winningBids.append(bid)
            else:
                lostBids.append(bid)
        else:
            openBids.append(bid)

    context = {
        'user': user,
        'openBids': openBids,
        'lostBids': lostBids,
        'winningBids': winningBids
    }
    return render(request, 'auction/profile.html', context)

@loginRequired
def expired(request):
    expiredItems = Item.objects.filter(endDateTime__lt=datetime.datetime.now())
    context = {
        'items': expiredItems
    }
    return render(request, 'auction/expired.html', context)
