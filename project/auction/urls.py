from django.urls import path

from . import views

urlpatterns = [
    path('listings/', views.listings, name='listings'),
    path('listings/<int:itemid>', views.listing, name='listing'),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('list/', views.list, name='list'),
    path('bids/', views.bids, name='bids')
]
