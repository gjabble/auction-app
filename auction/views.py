from django.shortcuts import render
from .models import Item, UserProfile, Bid, BasketItem
from django.http import JsonResponse
from django.core import serializers
from django.forms.models import model_to_dict
import json
from django.http import QueryDict
import datetime
from django.shortcuts import redirect
from django.core.mail import send_mail
from django.conf import settings
import uuid
from django import HttpResponse

def index(request):
    return redirect('/auction/listings')

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
        try:
            if request.session['username']:
                return redirect('/auction/listings')
            else:
                return render(request, 'auction/login.html')
        except:
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

def searchListings(request):
    search = request.GET.get('search')
    if search == '':
        items = Item.objects.filter(endDateTime__gt=datetime.datetime.now())
        results = serializers.serialize('json', items)
        return JsonResponse(results, safe=False)
    items = Item.objects.filter(endDateTime__gt=datetime.datetime.now())
    searchresults = items.filter(title__contains=search)
    results = serializers.serialize('json', searchresults)
    return JsonResponse(results, safe=False)

def listings(request):
    if request.method == 'POST':
        user = UserProfile.objects.get(username=request.session['username'])
        title = request.POST.get('title')
        description = request.POST.get('description')
        image = request.FILES.get('image')
        dateTime = request.POST.get('datetime')
        price = request.POST.get('price')
        auction = request.POST.get('auction')
        stock = request.POST.get('stock')
        if auction == 'false':
            auction = False
        else:
            auction = True
        if not stock:
            stock = 1
        item = Item(title=title, description=description, image=image, endDateTime=dateTime, userProfile=user, price=price, auction=auction, stock=stock)
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
        user = UserProfile.objects.get(username=request.session['username'])
        if item.userProfile == user:
            return JsonResponse({'error': 'You can not bid on your own listing'})
        if item.endDateTime.replace(tzinfo=None) < datetime.datetime.now():
            return JsonResponse({'error': 'This item has expired'})
        amount = request.POST.get('amount')
        try:
            relevantBids = Bid.objects.filter(item=item)
            highestBid = relevantBids.latest('amount')
            if highestBid.amount >= float(amount):
                return JsonResponse({'error': 'Bid is too low'})

            previousBidder = UserProfile.objects.get(pk=highestBid.userProfile)
            if not previousBidder == user:
                previousBidderEmail = previousBidder.email
                subject = "You've been outbid on " + item.title
                message = "You've been outbid on " + item.title + " at £" + amount + " " + " http://" + request.get_host() + "/auction/listings/" + str(item.id)
                email_from = settings.EMAIL_HOST_USER
                recipient_list = previousBidderEmail
                send_mail(subject, message, email_from, [recipient_list], fail_silently=False)

            item.price = amount
            bid = Bid(userProfile=user, item=item, amount=amount,bidDateTime=datetime.datetime.now())
            bid.save()
            item.save()

            return JsonResponse({'success': 'successfully created bid'})

        except Exception as e:
            if float(amount) <= item.price:
                return JsonResponse({'error': 'bid below starting price'})
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

def expired(request):
    expiredItems = Item.objects.filter(endDateTime__lt=datetime.datetime.now())
    context = {
        'items': expiredItems
    }
    return render(request, 'auction/expired.html', context)


def calculateTotals(basket):
    if not basket:
        return {'subtotal':'0.00', 'shipping': '0.00', 'total':'0.00'}
    subtotal = 0
    for item in basket:
        temp = Item.objects.get(pk=item.item.id)
        price = temp.price
        subtotal += price * item.quantity
    shipping = 3.50
    total = float(subtotal) + shipping
    return {
        'subtotal': subtotal,
        'shipping': str(shipping) + '0' ,
        'total': str(total) + '0',
    }

@loginRequired
def basket(request):
    def filterBasket(basket):
        user = UserProfile.objects.get(username=request.session['username'])
        try:
            for basketitem in basket:
                item = Item.objects.get(id=basketitem.item.id)
                if item.endDateTime.replace(tzinfo=None) < datetime.datetime.now():
                    outdatedBasketItems = BasketItem.objects.filter(item=item)
                    for outdateditem in outdatedBasketItems:
                        outdateditem.delete()
            return BasketItem.objects.filter(userProfile=user)
        except:
            return BasketItem.objects.filter(userProfile=user)


    if request.method == 'POST':
        item = Item.objects.get(pk=request.POST.get('itemId'))
        quantity = int(request.POST.get('quantity'))
        newstock = item.stock - quantity
        if newstock < 0:
            return JsonResponse({'error':'item is unavailable for that quantity', 'stock':item.stock})
        user = UserProfile.objects.get(username=request.session['username'])
        userbasket = BasketItem.objects.filter(userProfile=user)
        basketitem = userbasket.filter(item=item)
        item.stock = newstock
        if basketitem:
            basketitem = basketitem.first()
            basketitem.quantity = basketitem.quantity + quantity
            item.save()
            basketitem.save()
            return JsonResponse({'success':'successfully added to basket', 'stock':item.stock})
        else:
            basketitem = BasketItem(userProfile=user, item=item, quantity=quantity)
            basketitem.save()
            item.save()
            return JsonResponse({'success':'successfully added to basket', 'stock':item.stock})
    elif request.method == 'GET':
        user = UserProfile.objects.get(username=request.session['username'])
        basket = filterBasket(BasketItem.objects.filter(userProfile=user))
        response = calculateTotals(basket)
        response['items'] = basket
        return render(request, 'auction/basket.html', response)
    elif request.method == 'DELETE':
        data = QueryDict(request.body)
        itemid = data.get('itemId')
        basketItemId = data.get('basketItemId')
        basketitem = BasketItem.objects.get(pk=basketItemId)
        item = Item.objects.get(pk=itemid)
        quantity = basketitem.quantity
        item.stock = item.stock + quantity
        basketitem.delete()
        item.save()
        user = UserProfile.objects.get(username=request.session['username'])
        basket = BasketItem.objects.filter(userProfile=user)
        response = calculateTotals(basket)
        response['success'] = 'successfully removed basket item'
        response['basketItemId'] = basketItemId
        return JsonResponse(response)

@loginRequired
def checkout(request):
    orderid = uuid.uuid1()
    user = UserProfile.objects.get(username=request.session['username'])
    basket = BasketItem.objects.filter(userProfile=user)
    for item in basket:
        item.delete()
    context = calculateTotals(basket)
    context['orderid'] = orderid
    return render(request, 'auction/checkout.html', context)

def health(request):
    return HttpResponse('ok')
