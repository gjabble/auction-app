from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('listings/', views.listings, name='listings'),
    path('listings/<int:itemid>', views.listing, name='listing'),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('list/', views.listBid, name='list'),
    path('bids/', views.bids, name='bids'),
    path('profile/', views.profile, name='profile'),
    path('bids/<int:itemid>', views.bid, name='bid'),
    path('expired-listings/', views.expired, name='expired'),
    path('listings/search/', views.searchListings, name='search')
]
