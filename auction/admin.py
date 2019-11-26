from django.contrib import admin
from .models import UserProfile, Item, Bid, BasketItem
# Register your models here.
admin.site.register(UserProfile)
admin.site.register(Item)
admin.site.register(Bid)
admin.site.register(BasketItem)