def cleanPostRideRequest(request):
    if (request.method != "POST"):
        return (False, "You should send POST request")
    par = request.POST
    if "originID" not in par or "destinationID" not in par:
        return (False, "originID or destinationID Missed")
    if "originName" not in par or "destinationName" not in par:
        return (False, "originName or destinationName Missed")
    if "originLat" not in par or "originLng" not in par or "destinationLat" not in par\
        or "destinationLng" not in par:
        return (False, "origin or destination latitude or longitude Missed")
    else:
        originLat = par["originLat"]
        originLng = par["originLng"]
        destLat = par["destinationLat"]
        destLng = par["destinationLng"]
        try:
            olat = float(originLat)
            olng = float(originLng)
            dlat = float(destLat)
            dlng = float(destLng)
        except:
            return (False, "Illegal latitude or longitude")
    if "originAddress" not in par or "destinationAddress" not in par:
        return (False, "origin or destination address Missed")
    if "rideTime" not in par or not par['rideTime'].isdigit():
        return (False, "Missing or Illegal rideTime")
    if "rideType" not in par or (par["rideType"] != "Driver" and par["rideType"] != "Passenger"):
        return (False, "Missing rideType or Illegal rideType")
    if "message" not in par:
        return (False, "Missing message from user")
    return (True, "Success Clean the Post Ride request")

def cleanRefreshPostRequest(request):
    if (request.method != "GET"):
        return (False, "You should send GET request")
    par = request.GET
    if "originLat" not in par or "originLng" not in par or "destinationLat" not in par\
        or "destinationLng" not in par:
        return (False, "origin or destination latitude or longitude Missed")
    else:
        originLat = par["originLat"]
        originLng = par["originLng"]
        destLat = par["destinationLat"]
        destLng = par["destinationLng"]
        try:
            olat = float(originLat)
            olng = float(originLng)
            dlat = float(destLat)
            dlng = float(destLng)
        except:
            return (False, "Illegal latitude or longitude")
    if "rideTime" not in par:
        return (False, "Missing ride time for refresh")
    else:
        try:
            t = int(par["rideTime"])
        except:
            return (False, "Illegal ride time")
    return (True, "Success clean refresh post request")

def cleanAcceptRideRequest(request):
    if (request.method != "GET"):
        return (False, "You should send GET request")
    par = request.GET
    if "requestType" not in par:
        return (False, "Missing requestType")
    elif par['requestType'] != "accept":
        return (False, "You should send accept ride request")
    if "username" not in par:
        return (False, "Missing username")
    if "rideId" not in par:
        return (False, "Missing rideId")
    if "rideType" not in par:
        return (False, "Missing rideType")
    elif par["rideType"] != "Passenger" and par["rideType"] != "Driver":
        print par["rideType"]
        return (False, "Illegal rideType")
    return (True, "Success clean accept ride request")

def cleanConfirmRideRequest(request):
    print request.method
    if (request.method != "GET"):
        return (False, "You should send GET request")
    par = request.GET
    if "username" not in par:
        return (False, "Missing username")
    if "rideType" not in par:
        return (False, "Missing rideType")
    elif par['rideType'] != "Driver" and par['rideType'] != "Passenger":
        return (False, "Illegal rideType")
    if "rideId" not in par:
        return (False, "Missing rideId")
    if "messageId" not in par:
        return (False, "Missing messageId")
    elif not par['messageId'].isdigit():
        return (False, "Illegal messageId")
    return (True, "Success clean confirm ride request")

def cleanIgnoreMessageRequest(request):
    if (request.method != "GET"):
        return (False, "You should send GET request")
    par = request.GET
    if "messageId" not in par:
        return (False, "Missing messageId")
    elif not par['messageId'].isdigit():
        return (False, "Illegal messageId")
    return (True, "Success clean ignore messsage request")


def cleanAddFriendRequest(request):
    if (request.method != "POST"):
        return (False, "You should send POST request")
    par = request.POST
    if "username" not in par:
        return (False, "Missing username")
    return (True, "Success clean add friend request")

def cleanConfirmFriendRequest(request):
    if (request.method != "POST"):
        return (False, "You should send POST request")
    par = request.POST
    if "messageId" not in par:
        return (False, "Missing messageId")
    return (True, "Success clean confirm friend request")

def cleanCancelRideRequest(request):
    if (request.method != "POST"):
        return (False, "You should send POST request")
    par = request.POST
    if "rideId" not in par:
        return (False, "Missing rideId")
    elif not par['rideId'].isdigit():
        return (False, "Illegal rideId")
    if "rideType" not in par:
        return (False, "Missing rideType")
    elif par['rideType'] != "Driver" and par['rideType'] != "Passenger":
        return (False, "Illegal rideType")
    return (True, "Success clean cancel ride request")
