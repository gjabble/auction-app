from django.shortcuts import render
from .models import Item, UserProfile, Bid
from django.http import JsonResponse
from django.core import serializers
from django.forms.models import model_to_dict
import json
from django.http import QueryDict
import datetime


# Create your views here.
def loggedin(view):
    def check_loggedin(request):
        if 'username' in request.session:
            username = request.session['username']
            user = UserProfile.objects.get(username=username)
            return view(request)
        else:
            return render(request,'auction/login.html')
    return check_loggedin

def register(request):
    if(request.method == 'GET'):
        return render(request, 'auction/register.html')
    user = UserProfile(username = request.POST.get('username'),
                    password = request.POST.get('password'),
                    email = request.POST.get('email'),
                    dob = request.POST.get('dob'))
    user.save()
    return render(request, 'auction/login.html')

# def login(request):
#     if(request.method == 'GET'):
#         return render(request, 'auction/login.html')
#     else:
#         username = request.POST['username']
#         password = request.POST['password']
#
#         try:
#             user = UserProfile.objects.get(username=username)
#             if user.password == password:
#                 request.session['username'] = username
#                 request.session['password'] = password
#                 return JsonResponse({'message': 'successfully logged in'})
#             else:
#                 return JsonResponse({'message': 'Invalid username or password'})
#         except UserProfile.DoesNotExist:
#             return JsonResponse({'message': "Invalid username or password"})

def login(request):
    if(request.method == 'GET'):
        return render(request, 'auction/login.html')

    elif(request.method == 'POST'):
        try:
            username = request.POST['username']
            password = request.POST['password']
            user = UserProfile.objects.get(username = username)
            if password == user.password:
                request.session['username'] = username
                return JsonResponse({'message': 'Success', 'username': username, 'loggedin': True})
            else:
                return JsonResponse({'message': 'Invalid username or password'})
        except UserProfile.DoesNotExist:
            return JsonResponse({'message': 'Invalid username or password'})

def logout(request):
    request.session.flush()
    return render(request,'auction/login.html')

@loggedin
def listings(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        image = request.POST.get('image')
        dateTime = request.POST.get('dateTime')
        price = request.POST.get('price')
        # TODO - FIX UserProfile TO BE SET TO USER THAT REQUEST LISTINGS
        item = Item(title=title, description=description, image=image, endDateTime=dateTime, userProfile=UserProfile.objects.get(pk=1), price=price)
        item.save()
        return JsonResponse({'itemId': item.id})
    items = Item.objects.all()
    context = {
        'items': items
    }
    return render(request, 'auction/listings.html', context)

# @loggedin
def listing(request, itemid):
    item = Item.objects.get(pk=itemid)
    bids = Bid.objects.filter(item = itemid);
    context = {
        'item': item,
        'bids': bids
    }
    return render(request, 'auction/listing.html', context)

@loggedin
def list(request):
    return render(request, 'auction/list.html')

def bids(request):
    item = Item.objects.get(id=request.POST.get('itemId'))
    user = UserProfile.objects.get(id = request.POST.get('userId'))
    amount = request.POST.get('amount')
    item.price = amount
    bid = Bid(userProfile=user, item=item, amount=amount,bidDateTime=datetime.datetime.now())
    bid.save()
    item.save()
    return JsonResponse({'message':'successfully added bid'})
