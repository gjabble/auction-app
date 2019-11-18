from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
from django import forms

class UserProfile(User):
    dob = models.DateField(max_length=8)
    #email
    #username
    #password

    def __str__(self):
          return "username: " + self.username +  '\nemail:' + self.email + ", \ndob: " + str(self.dob)

class Item(models.Model):
  title = models.CharField(max_length=100)
  description = models.CharField(max_length=100)
  image = models.ImageField(upload_to='gallery', blank=True, null=True)
  endDateTime = models.DateTimeField(default=now, editable=True)
  userProfile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
  price = models.DecimalField(max_digits=8, decimal_places=2, default=0.99)

class Bid(models.Model):
  userProfile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
  item = models.ForeignKey(Item, on_delete=models.CASCADE)
  amount = models.DecimalField(max_digits=8, decimal_places=2)
  bidDateTime = models.DateTimeField()
