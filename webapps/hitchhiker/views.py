from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.core.urlresolvers import reverse
# Decorator to use built-in authentication system
from django.contrib.auth.decorators import login_required
# from django.utils.timezone import 
# Used to create and manually log in a user
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.http import HttpResponse, Http404, HttpResponseRedirect, JsonResponse
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail

from hitchhiker.models import *
from hitchhiker.forms import *
import time

from mimetypes import guess_type
from django.core import serializers
from datetime import datetime
from hitchhiker.models import *
from s3 import s3_upload, s3_delete
from hitchhiker.cleanRequest import *

import PIL
import json
from time import mktime


@login_required
def home(request):
    contex = {}
    selfProfile = Profile.objects.get(user = request.user)
    
    synchronizeRides()
    # actually these drivers and passengers will be refreshed regarding the location
    # of user after initialize the google map/
    contex['drivers'] = Driver.objects.filter(active = True)[:10]
    contex['passengers'] = Passenger.objects.filter(active = True)[:10]
    contex['selfProfile'] = selfProfile
    newMessageCount = len(selfProfile.messages.filter(active=True))
    contex['newMessageCount'] = newMessageCount
    return render(request, 'hitchhiker.html', contex)
# every time a user log in to the home page, the database will be synchronized.
# all out-of-date ride will be marked withh inactive
def synchronizeRides():
    now = time.time()
    for driver in Driver.objects.filter(active=True).filter(rideTime__lt=now):
        # print "inactive" + str(driver)
        driver.active = False
        driver.save()
    for passenger in Passenger.objects.filter(active=True).filter(rideTime__lt=now):
        # print passenger
        passenger.active = False
        passenger.save()    
# return the friends recommendation for the login user
def getRecommendation(self, topPlaces):
    rec = Profile.objects.filter(destinations__in = topPlaces).exclude(id__in = self.friends.values_list('id',flat=True))
    rec = set(rec)
    # print "rec" + str(rec)
    if (self in rec):
        rec.remove(self)
    # return 6 people at most
    return list(rec)[:6]
# return the places with biggest hotness
def getHotPlaces(self):
    # hotPlaces = Position.objects.all().exclude(gID__in = self.destinations.values_list('gID', flat = True)).order_by('hotness').reverse()
    hotPlaces = Position.objects.all().order_by('hotness').reverse()
    return hotPlaces[:6]

# return the place view
@login_required
def viewPlace(request):
    context = {}
    if request.method != "GET":
        return home(request)
    if "gID" not in request.GET:
        return home(request)
    gID = request.GET['gID']
    if (Position.objects.filter(gID = gID)):
        place = Position.objects.get(gID = gID)
        context['place'] = place
        visitors = Profile.objects.filter(destinations__in = [place])
        context['visitors'] = visitors
        reviews = place.reviews.filter(text_length__gt = 0).order_by('timeStamp').reverse()[:3]
        context['reviews'] = reviews
        selfProfile = Profile.objects.get(user = request.user)
        context['selfProfile'] = selfProfile
        newMessageCount = len(selfProfile.messages.filter(active=True))
        contex['newMessageCount'] = newMessageCount
        return render(request, 'place.html', context)
    else:
        return home(request)
# return the profile view
@login_required
def viewProfile(request):
    if (request.method != "GET"):
        return home(request)
    context = {}
    if 'username' in request.GET and Profile.objects.filter(user__username = request.GET['username']):
        selfProfile = Profile.objects.get(user = request.user)
        context['selfProfile'] = selfProfile
        username = request.GET['username']
        profile = Profile.objects.get(user__username = username) # profileUsername
        context['profile'] = profile
        topPlaces = profile.destinations.all() #this will return all the visited places
        context['topPlaces'] = topPlaces
        context['currentDriverRide'] = Driver.objects.filter(active=True).filter(profile = profile)
        context['currentPassengerRide'] = Passenger.objects.filter(active=True).filter(profile = profile)
        newMessageCount = len(selfProfile.messages.filter(active=True))
        context['newMessageCount'] = newMessageCount
        if (request.user == profile.user):
            context['recFriends'] = getRecommendation(profile, topPlaces)
            context['hotPlaces'] = getHotPlaces(profile)
            context['editOption'] = True
        return render(request, 'profile.html', context)
    else:
        return home(request)
# this works for static image version ----- deprecated
# @login_required
# def UploadPicture(request):
#     username = request.GET['username']
#     user = get_object_or_404(User, username=username)
#     profile = get_object_or_404(Profile, user=user)
#     if not profile.picture:
#         raise Http404
#     content_type = guess_type(profile.picture.name)
#     return HttpResponse(profile.picture, content_type=content_type)

@transaction.atomic
@login_required
def EditProfile(request):
    context = {}
    username = request.user.username
    context['username'] = username
    user = get_object_or_404(User, username=username)

    if request.method == "GET":
        profile = user.profile_owner.all()[0]
        #profile = user.profile.all()[0]
        context['form'] = EditProfileForm(instance=profile)
        return render(request, 'editprofile.html', context)

    profile = Profile.objects.select_for_update().get(user=request.user)
    form = EditProfileForm(request.POST, request.FILES, instance=profile)
    # hren
    context['form'] = form
    if not form.is_valid():
        return render(request, 'editprofile.html', context)
    form.save()
    # upload picture to s3
    if form.cleaned_data['picture']:
            url = s3_upload(form.cleaned_data['picture'], profile.id)
            profile.pictureUrl = url
            profile.save()
            # print url
    return redirect(reverse('viewProfile') + '?username=' + request.user.username)

@transaction.atomic
def register(request):
    context = {}
    if request.method == 'GET':
        context['form'] = RegisterForm()
        return render(request, 'register.html', context)
    
    form = RegisterForm(request.POST)
    context['form'] = form
    
    if not form.is_valid():
        return render(request, 'register.html', context)
    
    # At this point, the form data is valid. Register and login the user.
    new_user = User.objects.create_user(
                                         username=form.cleaned_data['username'],
                                         password=form.cleaned_data['password1'],
                                         email=form.cleaned_data['email'])
    # Mark the user as inactive to prevent login before email confirmation.
    new_user.is_active = False
    new_user.save()
    
    # Generate a one-time user token and an email message body
    token = default_token_generator.make_token(new_user)
    
    email_body = """
Welcome to hitchhiker. Please click the link below to verify your email address and complete the registration of your account: http://%s%s """ % (request.get_host(),
                                     reverse('confirm', args=(new_user.username, token)))
                                    
    send_mail(subject="Verify your email address",
               message=email_body,
               from_email="hren@andrew.cmu.edu",
               recipient_list=[new_user.email]) 
    
    context['email'] = form.cleaned_data['email']
    defaultImg = "https://encrypted-tbn3.gstatic.com/images?q=tbn:ANd9GcQ6NWHG8jQRHsrF0UGjOCnewcfJNBq1qHPlz2tSPvK-tsCnkeoe"
    new_profile = Profile(
                          user=new_user,                            # user is the ForeignKey
                          fName=form.cleaned_data['firstname'],
                          lName=form.cleaned_data['lastname'],
                          age=form.cleaned_data['age'],
                          shortBio=form.cleaned_data['bio'],
                          email=form.cleaned_data['email'],
                          pictureUrl = defaultImg)
    new_profile.save()
    
    return render(request, 'needs-confirmation.html', context)

@transaction.atomic
def confirm_registration(request, username, token):

    user = get_object_or_404(User, username=username)
    
    # Send 404 error if token is invalid
    if not default_token_generator.check_token(user, token):
        raise Http404
        
    # Otherwise token was valid, activate the user.

    user.is_active = True
    user.save()

    return render(request, 'confirmed.html', {})
#check: parameters in the request
#this should be invoked by a post
@login_required
def postRide(request):
    response = {}
    checkRequestResult = cleanPostRideRequest(request)
    if(not checkRequestResult[0]):
        response["status"] = False
        response["info"] = checkRequestResult[1]
        return JsonResponse([response], safe=False)


    rideType = request.POST['rideType']#driver or passenger

    origin = getPosition(request.POST['originID'], request.POST['originName'], 
            request.POST['originLat'], request.POST['originLng'], 
            request.POST['originImg'], request.POST['originAddress'])
    destination = getPosition(request.POST['destinationID'], request.POST['destinationName'],
        request.POST['destinationLat'], request.POST['destinationLng'],
        request.POST['destinationImg'], request.POST['destinationAddress'])
    # illegal reviews should not stop posting ride
    if "originReviews" in request.POST:
        try:
            originReviews = json.loads(request.POST['originReviews'])
            updateReviews(origin, originReviews)
        except:
            print "illegal reviews"
    if "destinationReviews" in request.POST:
        try:
            destinationReviews = json.loads(request.POST['destinationReviews'])
            updateReviews(destination, destinationReviews)
        except:
            print "illegal reviews"

    profile = Profile.objects.get(user=request.user)
    addDestinations(profile, origin)
    addDestinations(profile, destination)

    rideTime = int(request.POST['rideTime']) #convert est to utc
    rideTimeStr = parseRideTime(rideTime)
    newRide = None
    message = request.POST['message']
    if (rideType == 'Driver'):
        newRide = Driver(profile=profile, origin = origin, destination = destination, 
            rideTime = rideTime/1000, rideTimeStr = rideTimeStr, message = message)
        newRide.save()
    else:
        newRide = Passenger(profile=profile, origin = origin, destination = destination, 
            rideTime = rideTime/1000, rideTimeStr = rideTimeStr, message = message)
        newRide.save()

    response['status'] = True
    response['info'] = "Successfully Post Ride " + str(newRide)
    response['username'] = request.user.username
    response['rideType'] = rideType
    response['rideId'] = newRide.id
    response['rideTime'] = rideTimeStr
    response['name'] = str(profile)
    response['pictureUrl'] = profile.pictureUrl
    response['origin'] = newRide.origin.name
    response['destination'] = newRide.destination.name
    response['message'] = message
    response['isSelf'] = True
    return JsonResponse([response], safe=False)
def getPosition(gID, name, lat, lng, imgUrl, addr):
    if (Position.objects.filter(gID=gID)):
        place = Position.objects.get(gID=gID)
        place.hotness += 1
        place.save()
    else:
        place = Position(gID = gID, name = name, 
                    longitude = lng, latitude = lat,
                    imgUrl = imgUrl, address = addr)
        place.save()
    return place

def addDestinations(profile, place):
    profile.destinations.add(place)
# this function parse the time from integer to str representation
# this will enable relatively representation format of time
def parseRideTime(rideTime):
    time = datetime.fromtimestamp(rideTime/1000)
    return str(time)
# update reviews for a given place according to timestamp, reviews is a json array
def updateReviews(place, reviews):
    for review in reviews:
        timeStamp = int(review['time'])
        if (not place.reviews.all().filter(timeStamp = timeStamp)):
            newReview = Review(timeStamp = timeStamp, text = review['text'],
                author = review['author_name'], rating = float(review['rating']),
                text_length = len(review['text']))
            newReview.save()
            place.reviews.add(newReview)
            place.save()
#this is automatilcally invoked to refresh the page, asking for a json file
@login_required
def refreshPost(request):
    response = {}
    result = cleanRefreshPostRequest(request)
    if (not result[0]):
        response['status'] = False
        response['info'] = result[1]
        return JsonResponse([response],safe=False)
    originLat = float(request.GET['originLat'])
    originLng = float(request.GET['originLng'])
    destinationLat = float(request.GET['destinationLat'])
    destinationLng = float(request.GET['destinationLng'])
    rideTime = int(request.GET['rideTime'])
    drivers = filterRide(originLat, originLng, destinationLat, destinationLng, rideTime, 'Driver')
    passengers = filterRide(originLat, originLng, destinationLat, destinationLng, rideTime, 'Passenger')
    driversList = []
    passengersList = []
    for driver in drivers:
        d = {}
        d['username'] = driver.profile.user.username
        d['name'] = str(driver.profile.fName) + " " + str(driver.profile.lName)
        d['pictureUrl'] = driver.profile.pictureUrl
        d['rideId'] = driver.id
        d['origin'] = driver.origin.name
        d['destination'] = driver.destination.name
        d['rideTime'] = driver.rideTimeStr#this may encounter format problem
        d['rideType'] = "Driver"
        d['message'] = driver.message
        if (driver.profile.user == request.user):
            d['isSelf'] = True
        else:
            d['isSelf'] = False
        driversList.append(d)
    for passenger in passengers:
        d = {}
        d['username'] = passenger.profile.user.username
        d['name'] = str(passenger.profile.fName) + " " + str(passenger.profile.lName)
        d['pictureUrl'] = passenger.profile.pictureUrl
        d['rideId'] = passenger.id
        d['origin'] = passenger.origin.name
        d['destination'] = passenger.destination.name
        d['rideTime'] = passenger.rideTimeStr#this may encounter format problem
        d['rideType'] = "Passenger"
        d['message'] = passenger.message
        if (passenger.profile.user == request.user):
            d['isSelf'] = True
        else:
            d['isSelf'] = False
        passengersList.append(d)
    response['status'] = True
    response['drivers'] = driversList
    response['passengers'] = passengersList
    return JsonResponse([response], safe=False)

# we disable the filter via ride time, since most people's schedule about a ride is quite flexiable
def filterRide(originLat, originLng, destinationLat, destinationLng, rideTime, rideType):
    latDif = 0.01
    lngDif = 0.01
    # timeDif = 3600 #disabled since most user's ride sould be flexible
    if (rideType == "Driver"):
        drivers = Driver.objects.filter(active = True)\
            .filter(origin__latitude__lte = (originLat + latDif))\
            .filter(origin__latitude__gte = (originLat - latDif))\
            .filter(origin__longitude__lte = (originLng + lngDif))\
            .filter(origin__longitude__gte = (originLng - lngDif))\
            .filter(destination__latitude__lte = (destinationLat + latDif))\
            .filter(destination__latitude__gte = (destinationLat - latDif))\
            .filter(destination__longitude__lte = (destinationLng + lngDif))\
            .filter(destination__longitude__gte = (destinationLng - lngDif))
        return drivers
    else:
        passengers = Passenger.objects.filter(active = True)\
            .filter(origin__latitude__lte = (originLat + latDif))\
            .filter(origin__latitude__gte = (originLat - latDif))\
            .filter(origin__longitude__lte = (originLng + lngDif))\
            .filter(origin__longitude__gte = (originLng - lngDif))\
            .filter(destination__latitude__lte = (destinationLat + latDif))\
            .filter(destination__latitude__gte = (destinationLat - latDif))\
            .filter(destination__longitude__lte = (destinationLng + lngDif))\
            .filter(destination__longitude__gte = (destinationLng - lngDif))
        return passengers
@login_required 
#this method will be called when person A accept B's ride, and B confirm or reject the acceptance
def processAcceptRideRequest(request):
    response = {}
    result = cleanAcceptRideRequest(request)
    if (not result[0]):
        response['status'] = True
        response['info'] = result[1]
        return JsonResponse([response], safe = False)
    requestType = request.GET['requestType']
    # the username of receiver
    username = request.GET['username']
    rideId = request.GET['rideId']
    rideType = request.GET['rideType']
    #get the ride
    if (rideType == 'Passenger'):
        ride = Passenger.objects.get(id=rideId)
    else:
        ride = Driver.objects.get(id=rideId)
    if (not ride.active):
        response['status'] = False
        response['info'] = "This ride is no longer available"
        return JsonResponse([response], safe=False)
    receiver = ride.profile
    sender = Profile.objects.get(user=request.user)
    if (receiver == sender):
        response['status'] = False
        response['info'] = "You cannot accept your own ride"
        return JsonResponse([response], safe=False)

    text = "Acceptance: Your ride as " + rideType + " " + str(ride) \
        + " has been accepted by " + sender.fName + " " + sender.lName
    message = Message(sender = sender, text = text, messageType = "accept", 
        rideType = rideType, rideId = rideId, active = True)
    message.save()
    receiver.messages.add(message)
    receiver.save()
    response['status'] = True
    response['info'] = "You accept the ride " + str(ride) + " from " + str(receiver)
    return JsonResponse([response], safe=False)
@login_required 
def processConfirmRideRequest(request):
    response = {}
    result = cleanConfirmRideRequest(request)
    if (not result[0]):
        response['status'] = False
        response['info'] = result[1]
        return JsonResponse([response], safe=False)
    # start check legal parameter
    username = request.GET['username']
    rideType = request.GET['rideType']
    rideId = int(request.GET['rideId'])
    if (rideType == 'Driver'):
        if (not Driver.objects.filter(id=rideId)):
            response['status'] = False
            response['info'] = "Cannot find specified ride"
            return JsonResponse([response], safe=False)
        ride = Driver.objects.get(id = rideId)
    else:
        if (not Passenger.objects.filter(id=rideId)):
            response['status'] = False
            response['info'] = "Cannot find specified ride"
            return JsonResponse([response], safe=False)
        ride = Passenger.objects.get(id = rideId)

    if (Profile.objects.filter(user__username = username)):
        receiver = Profile.objects.get(user__username = username)
    else:
        response['status'] = False
        response['info'] = "Cannot find specified user"
        return JsonResponse([response], safe=False)

    messageId = int(request.GET['messageId'])
    sender = Profile.objects.get(user = request.user)
    if (sender.messages.all().filter(id = messageId)):
        currentMessage = sender.messages.all().get(id = messageId)
        if (not currentMessage.active):
            response['status'] = False
            response['info'] = "This is message is no longer available"
            return JsonResponse([response], safe=False)
    else:
        response['status'] = False
        response['info'] = "Cannot find specified message"
        return JsonResponse([response], safe=False)
    if (not ride.active):
        response['status'] = False
        response['info'] = "This ride is no longer available"
        currentMessage.active = False
        currentMessage.save()
        return JsonResponse([response], safe=False)
    # end check parameters
    # start confirm ride
    
    text = "Confirm: Your ride " + str(ride) + " has been confirmed by " + \
            sender.fName + " " + sender.lName
    message = Message(sender = sender, text = text, messageType = "confirm", 
        rideType = rideType, rideId = rideId, active = True)
    message.save()
    receiver.messages.add(message)
    receiver.save()
    origin = ride.origin
    destination = ride.destination
    addDestinations(receiver, origin)
    addDestinations(receiver, destination)
    if (rideType == 'Driver'):
        driver = sender
        passenger = receiver
    else:
        driver = receiver
        passenger = sender
    
    ride.active = False
    ride.save()
    currentMessage.active = False
    currentMessage.save()
    response['status'] = True
    response['info'] = "Successfully confirm the ride" + str(ride) + " for " +\
                 str(receiver) + ", please check your mail box for detail"
    sendConfirmRideEmail(driver, passenger, ride)
    return JsonResponse([response], safe= False)
@login_required 
def sendConfirmRideEmail(driver, passenger, ride):
    driver_email = "You have confirmed a ride " + str(ride) + ", please pick your passenger " + passenger.fName + " " + passenger.lName
    passenger_email = "You have confirmed a ride " + str(ride) + ", please wait for your driver " + driver.fName + " " + driver.lName
                  
    send_mail(subject="Confirm your ride",
               message=driver_email,
               from_email="jianhaol@andrew.cmu.edu",
               recipient_list=[driver.email])
    send_mail(subject="Confirm your ride",
               message=passenger_email,
               from_email="jianhaol@andrew.cmu.edu",
               recipient_list=[passenger.email])
@login_required 
def processIgnoreMessageRequest(request):
    response = {}

    result = cleanIgnoreMessageRequest(request)
    if (not result[0]):
        response['status'] = False
        response['info'] = result[1]
        return JsonResponse([response], safe=False)
    messageId = int(request.GET['messageId'])
    if (Message.objects.filter(id = messageId)):
        # inactive the message
        message = Message.objects.get(id = messageId)
        message.active = False
        message.save()
        # if this message is an accept message, send back a message to the sender that his accept has been ignored
        messageType = request.GET['messageType']
        if (messageType == 'accept'):
            rideType = request.GET['rideType']
            rideId = int(request.GET['rideId'])
            if (rideType == 'Driver'):
                ride = Driver.objects.get(id = rideId)
            else:
                ride = Passenger.objects.get(id = rideId)
            receiver = Profile.objects.get(user__username = request.GET['receiverUsername'])
            sender = Profile.objects.get(user=request.user)
            text = "Rejection: Your request " + str(ride) + "has been rejected"
            message = Message(sender = sender, text = text, messageType = "reject", 
                    rideType = rideType, rideId = rideId, active = True)
            message.save()
            receiver.messages.add(message)
            receiver.save()
        response = {}
        response['status'] = True
        response['info'] = "You have ignored a message"
        return JsonResponse([response], safe=False)
    else:
        response = {}
        response['status'] = False
        response['info'] = 'Cannot find the specified message'
        return JsonResponse([response], safe=False)
    # return home(request)
@login_required
#this will process a "addFriendsRequest" by sending a request to the "friend" and waiting for confirmation
def processAddFriendRequest(request):
    response = {}
    result = cleanAddFriendRequest(request)
    if (not result[0]):
        response['status'] = False
        response['info'] = result[1]
        return JsonResponse([response], safe=False)

    username = request.POST['username']
    if (Profile.objects.filter(user__username = username)):
        receiver = Profile.objects.get(user__username = username)
    else:
        response['status'] = False
        response['info'] = "Cannot find the specified user"
        return JsonResponse([response], safe=False)
    sender = Profile.objects.get(user = request.user)
    text = sender.fName + " " + sender.lName + " send an invitation to you"
    message = Message(sender = sender, text = text, messageType = "friendInvitation", rideType = "None",
            rideId = -1, active = True)
    message.save()
    receiver.messages.add(message)
    receiver.save()
    response = {}
    response['status'] = True
    response['info'] = 'You have sent an invitation to ' + str(receiver)
    return JsonResponse([response], safe=False)
@login_required
def processConfirmFriendRequest(request):
    response = {}
    result = cleanConfirmFriendRequest(request)
    if (not result[0]):
        response['status'] = False
        response['info'] = result[1]
        return JsonResponse([response], safe=False)
    messageId = request.POST['messageId']
    if (Message.objects.filter(id = messageId)):
        message = Message.objects.get(id = messageId)
    else:
        response['status'] = False
        response['info'] = 'Cannot find specified message'
        return JsonResponse([response], safe=False)
    message.active = False
    message.save()
    receiver = message.sender
    sender = Profile.objects.get(user = request.user)
    #send the confirmation message
    text = sender.fName + " " + sender.lName + " has confirmed your invitation"
    newMessage = Message(text = text, sender = sender, messageType = "confirmInvitation", rideType = "None", 
                    rideId = -1, active = True)
    newMessage.save()
    receiver.messages.add(newMessage)
    #add each other to friends list
    receiver.friends.add(sender)
    receiver.save()
    sender.friends.add(receiver)
    sender.save()
    response['status'] = True
    response['info'] = 'Successfully add friend ' + str(receiver)
    return JsonResponse([response], safe=False)
@login_required
def processCancelRideRequest(request):
    response = {}
    result = cleanCancelRideRequest(request)
    if (not result[0]):
        response['status'] = False
        response['info'] = result[1]
        return JsonResponse([response], safe=False)
    rideId = int(request.POST['rideId'])
    rideType = request.POST['rideType']
    if (rideType == "Driver"):
        if (Driver.objects.filter(id = rideId)):
            ride = Driver.objects.get(id = rideId)
        else:
            response['status'] = False
            response['info'] = "Cannot find specified ride"
    else:
        if (Passenger.objects.filter(id = rideId)):
            ride = Passenger.objects.get(id = rideId)
        else:
            response['status'] = False
            response['info'] = "Cannot find specified ride"
    ride.active = False
    ride.save()
    response['status'] = True
    response['info'] = "Successfully inactive ride " + str(ride)
    return JsonResponse([response], safe=False)