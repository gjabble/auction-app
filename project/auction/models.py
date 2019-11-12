from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now

class UserProfile(User):
  dob = models.DateField(max_length=8)

class Item(models.Model):
  title = models.CharField(max_length=100)
  description = models.CharField(max_length=100)
  image = models.ImageField(upload_to='images', blank=True, null=True)
  endDateTime = models.DateTimeField(default=now, editable=True)
  userProfile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)

class Bid(models.Model):
  userProfile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
  item = models.ForeignKey(Item, on_delete=models.CASCADE)
  amount = models.DecimalField(max_digits=8, decimal_places=2)
  bidDateTime = models.DateTimeField()
