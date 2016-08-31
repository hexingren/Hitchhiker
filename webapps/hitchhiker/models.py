from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from datetime import datetime

# Create your models here.
class Position(models.Model):
    gID = models.CharField(max_length = 255, primary_key=True)
    name = models.CharField(max_length = 255)
    imgUrl = models.CharField(max_length = 256,blank=True, null = True)
    address = models.CharField(max_length= 256, blank = True)
    longitude = models.FloatField()
    latitude = models.FloatField()
    hotness = models.IntegerField(default = 1)
    reviews = models.ManyToManyField('Review', blank = True, related_name = "position_reviews")
    def __unicode__(self):
        return self.name
class Review(models.Model):
    timeStamp = models.BigIntegerField()
    text = models.CharField(max_length = 1024)
    author = models.CharField(max_length = 30)
    rating = models.FloatField()
    text_length = models.IntegerField()
    def __unicode__(self):
        return self.text
#this class is just a message sent to user
class Message(models.Model):
    sender = models.ForeignKey('Profile', related_name = 'message_sender')

    text = models.CharField(max_length = 255)
    messageType = models.CharField(max_length = 30)
    # either driver or passenger, actually, every message is regarding a single ride posted
    rideType = models.CharField(max_length = 30)
    # the id of driver or passenger
    rideId = models.IntegerField()
    # active or inactive
    active = models.BooleanField()
    def __unicode__(self):
        return str(self.messageType) + ": " + str(self.text)


class Profile(models.Model):
    user = models.ForeignKey(User, related_name = 'profile_owner')
    lName = models.CharField(max_length = 30, blank = True, null = True)
    fName = models.CharField(max_length = 30, blank = True, null = True)
    age = models.IntegerField(default = 0, blank = True, null = True)
    shortBio = models.CharField(default = 'This man leaves nothing', max_length = 430, blank = True, null = True)
    email = models.CharField(max_length= 40, blank = True, null = True)
    friends = models.ManyToManyField('Profile', related_name = 'profile_friends', blank=True)
    pictureUrl = models.CharField(max_length = 256,blank=True, null = True)
    destinations = models.ManyToManyField(Position, related_name = 'profile_destinations', blank = True)
    messages = models.ManyToManyField(Message, related_name='profile_messages')
    def __unicode__(self):
        return self.fName + " " + self.lName

class Driver(models.Model):
    profile = models.ForeignKey(Profile, related_name = 'driver_profile')
    origin = models.ForeignKey(Position, related_name = 'driver_origin')
    destination = models.ForeignKey(Position, related_name = 'driver_destination')
    message = models.CharField(max_length = 256, blank = True)
    rideTime = models.IntegerField(blank = True)
    rideTimeStr = models.CharField(max_length = 255, blank = True)
    active = models.BooleanField(default = True, blank = True)
    def __unicode__(self):
        return "from " + str(self.origin) + " to " + str(self.destination)


class Passenger(models.Model):
    profile = models.ForeignKey(Profile, related_name = 'passenger_profile')
    origin = models.ForeignKey(Position, related_name = 'passenger_origin')
    destination = models.ForeignKey(Position, related_name = 'passenger_destination')
    message = models.CharField(max_length = 256, blank = True)
    rideTime = models.IntegerField(blank = True)
    rideTimeStr = models.CharField(max_length = 255, blank = True)
    active = models.BooleanField(default=True, blank = True)
    def __unicode__(self):
        return "from " + str(self.origin) + " to " + str(self.destination)
