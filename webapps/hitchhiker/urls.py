from django.conf.urls import include, url
from django.contrib.auth import views as auth_views
from hitchhiker import views as private_views
# import hitchhiker.url
urlpatterns = [
    url(r'^$', private_views.home, name='home'),
    url(r'^refreshPost', private_views.refreshPost, name='refreshPost'),
    url(r'^login', auth_views.login, {'template_name':'login.html'}, name='login'),
    url(r'^logout', auth_views.logout_then_login, name='logout'),
    url(r'^register', private_views.register, name='register'),
    url(r'^confirm-registration/(?P<username>[a-zA-Z0-9_@\+\-]+)/(?P<token>[a-z0-9\-]+)$', private_views.confirm_registration, name='confirm'),
    url(r'^post-ride', private_views.postRide, name='postRide'),
    url(r'^profile', private_views.viewProfile, name = 'viewProfile'),
    url(r'^place', private_views.viewPlace, name = 'viewPlace'),
    url(r'^process-acceptRide-request+', private_views.processAcceptRideRequest, name='processAcceptRequest'),
    url(r'^process-confirmRide-request+', private_views.processConfirmRideRequest, name='processConfirmRequest'),
    url(r'^editprofile', private_views.EditProfile, name='editprofile'),
    url(r'^process-ignoreMessage-request+', private_views.processIgnoreMessageRequest, name='processIgnoreMessageRequest'),
    url(r'^process-addFriend-request+', private_views.processAddFriendRequest, name='processAddFriendRequest'),
    url(r'^process-confirmFriend-request+', private_views.processConfirmFriendRequest, name='processConfirmFriendRequest'),
    url(r'^process-cancelRide-request+', private_views.processCancelRideRequest, name='processCancelRideRequest'),
]
