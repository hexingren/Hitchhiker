/*
 * created by Team10.JianhaoLyu@webapps.S16.
 */

var origin;
var destination;
var map;
var placeService;
var directionService;
//this function must be called with the call back after loading google libraries
function initMap() {
    //set current position as the center of the map
    map = new google.maps.Map(document.getElementById('map'), {
        center: {lat: -34.397, lng: 150.644},
        zoom: 12
    });
    //init services
    var directionsDisplay = new google.maps.DirectionsRenderer;
    directionsService = new google.maps.DirectionsService;
    directionsDisplay.setMap(map);
    placeService = new google.maps.places.PlacesService(map);
    //info  window for every tag
    var infoWindow = new google.maps.InfoWindow({map: map});

    // Try HTML5 geolocation.
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function(position) {
            var pos = {
                lat: position.coords.latitude,
                lng: position.coords.longitude
            };
          map.setCenter(pos);
          refreshPost(position.coords.latitude,position.coords.longitude,position.coords.latitude,position.coords.longitude,(new Date()).getTime())

        }, function() {
            handleLocationError(true, infoWindow, map.getCenter());
        });
     } else {
        // Browser doesn't support Geolocation
        handleLocationError(false, infoWindow, map.getCenter());
    }


    //set the origin and destination
    var originInput = document.getElementById('originInput');
    var destinationInput = document.getElementById('destinationInput');
    var rideTimeInput =  document.getElementById('rideTimeInput');
    // rideTime = rideTimeInput.value;

    var originAutocomplete = new google.maps.places.Autocomplete(originInput);
    var destinaionAutocomplete = new google.maps.places.Autocomplete(destinationInput);

    originAutocomplete.bindTo('bounds', map);
    destinaionAutocomplete.bindTo('bounds', map);

    //add input onto map

    map.controls[google.maps.ControlPosition.TOP_RIGHT].push(document.getElementById('modal'));
    map.controls[google.maps.ControlPosition.TOP_RIGHT].push(destinationInput);
    map.controls[google.maps.ControlPosition.TOP_RIGHT].push(originInput);

    
    var originInfoWindow = new google.maps.InfoWindow();
    var destinationInfoWindow = new google.maps.InfoWindow();

    //create marker
    var originMarker = new google.maps.Marker({
          map: map,
          label:'o'
        });
    var destinationMarker = new google.maps.Marker({
          map: map,
          label:'d'
        });
    //add listener to marker
    originMarker.addListener('click', function() {
          originInfoWindow.open(map, marker);
        });
    destinationMarker.addListener('click', function() {
          destinationInfoWindow.open(map, marker);
        });
    //add listner to auto complete
    addListenerToAutocomplete(originAutocomplete, map, originMarker, originInfoWindow,
                                'origin', directionsDisplay);
    addListenerToAutocomplete(destinaionAutocomplete, map, destinationMarker,
                                destinationInfoWindow, 'destination', directionsDisplay);

}
function addListenerToAutocomplete(autocomplete, map, marker, infowindow, type, directionsDisplay) {
    // window.alert("add listener");
    autocomplete.addListener('place_changed', function() {
        infowindow.close();
        var place = autocomplete.getPlace();
        if (!place.geometry) {
            return;
        }

        if (place.geometry.viewport) {
            map.fitBounds(place.geometry.viewport);
        } else {
            map.setCenter(place.geometry.location);
            map.setZoom(17);
        }
      // Set the position of the marker using the place ID and location.
        marker.setPlace({
            placeId: place.place_id,
            location: place.geometry.location
        });
        marker.setVisible(true);
        infowindow.setContent('<div><strong>' + place.name + '</strong><br>' +
            place.formatted_address);
        infowindow.open(map, marker);

        if (type == "origin") {
            origin = place;
        }
        if (type == "destination") {
            destination = place;
        }
        if (origin && destination) {
            calculateDirection(directionsService, directionsDisplay);
            refreshPost(origin.geometry.location.lat(), origin.geometry.location.lng(),
            destination.geometry.location.lat(),destination.geometry.location.lng(),
                        (new Date()).getTime());
        }
    });
}
function calculateDirection(directionsService, directionsDisplay) {
    directionsService.route({
          origin: {'placeId':origin.place_id},
          destination: {'placeId':destination.place_id},  

          travelMode: google.maps.TravelMode['DRIVING'] //this only support driving
        }, function(response, status) {
          if (status == google.maps.DirectionsStatus.OK) {
            directionsDisplay.setDirections(response);
          } else {
            window.alert('Directions request failed due to ' + status);
          }
    });
}
function refreshPost(originLat, originLng, destLat, destLng, rideTime) {

    //send refresh request
    // console.log("refreshPost");
    if (window.XMLHttpRequest) {
        refreshReq = new XMLHttpRequest();
    } else {
        refreshReq = new ActiveXObject("Microsoft.XMLHTTP");
    }
    var milliSeconds = new Date().getTime()
    refreshReq.onreadystatechange = function() {
        if (refreshReq.readyState != 4) return;
        if (refreshReq.status != 200) return;
        var response = JSON.parse(refreshReq.responseText);
        var status = response[0]['status'];
        if (!status) {
            window.alert(response[0]["info"]);
            return;
        }
        update(response[0]);
    }
    var request = "/refreshPost?originLat=" + originLat + "&originLng=" + originLng + 
    "&destinationLat=" + destLat + "&destinationLng=" + destLng + "&rideTime=" + rideTime;
    refreshReq.open("GET", request, true);
    refreshReq.send(); 
}

function update(response) {
    drivers = response['drivers'];
    passengers = response['passengers'];

    var driverList;
    var passengerList;
    driverList = document.getElementById("driverList");
    passengerList = document.getElementById("passengerList");
    while (driverList.firstChild) {
        driverList.removeChild(driverList.firstChild);
    }
    while (passengerList.firstChild) {
        passengerList.removeChild(passengerList.firstChild);
    }
    for (var i = 0; i < drivers.length; i++) {
        addPostToList(drivers[i], driverList);
    }
    for (var i = 0; i < passengers.length; i++) {
        addPostToList(passengers[i], passengerList);
    }
}

function addPostToList(ride, list) {
    var originName = ride['origin'];
    var destinationName = ride['destination'];
    var rideTime = ride['rideTime'];
    var username = ride['username'];
    var rideId = ride['rideId'];
    var rideType = ride['rideType'];
    var pictureUrl = ride['pictureUrl'];
    var name = ride['name'];
    var message = ride['message'];
    var isSelf = ride['isSelf'];
    // var pictureUrl = "https://img.mengniang.org/common/b/b2/Shiki.jpg";

    var tr = document.createElement("tr");
    var d1 = document.createElement("td");
    var d2 = document.createElement("td");
    var d3 = document.createElement("td");
    var d4 = document.createElement("td");
    
    var d5 = document.createElement("td");
    d1.setAttribute("class", "d1");
    d2.setAttribute("class", "d2");
    d3.setAttribute("class", "d3");
    d4.setAttribute("class", "d4");
    d5.setAttribute("class", "d5");
    
    var a = document.createElement("a");
    var img = document.createElement("img");
    var nameSpan = document.createElement("span");
    var hoverDiv = document.createElement("div");
    var d4Child = document.createElement("div");
    var h = document.createElement("h5");
    var p = document.createElement("p");
    a.setAttribute("href", "/profile?username=" + username);
    img.setAttribute("src", pictureUrl);
    img.setAttribute("width", "30");
    img.setAttribute("height", "30");
    nameSpan.innerHTML = name;
    a.appendChild(img);
    a.appendChild(nameSpan);
    hoverDiv.setAttribute("class", "userInfo");
    h.innerHTML = name + " says:";
    p.innerHTML = message;
    hoverDiv.appendChild(h);
    hoverDiv.appendChild(p);

    d4Child.setAttribute("class", "user");
    d4Child.appendChild(a);
    d4Child.appendChild(hoverDiv);


    var confirmButton = document.createElement("button");
    confirmButton.setAttribute("class", "btn btn-default btn-s");
    if (!isSelf) {
        confirmButton.addEventListener("click", function() {sendAcceptRideRequest(username,rideId,rideType)});
        confirmButton.innerHTML = "Accept";
    } else {
        confirmButton.addEventListener("click", function() {sendCancelRideRequest(rideId, rideType, confirmButton)})
        confirmButton.innerHTML = "Cancel"
    }
    d1.innerHTML = rideTime;
    d2.innerHTML = originName;
    d3.innerHTML = destinationName;
    d4.appendChild(d4Child);
    d5.appendChild(confirmButton);

    tr.appendChild(d1);
    tr.appendChild(d2);
    tr.appendChild(d3);
    tr.appendChild(d4);
    tr.appendChild(d5);

    list.appendChild(tr);
    activeHover();
}

// hren mainpage input
function showInput() {
  var startingPoint =  document.getElementById("originInput").value;
  var destination =  document.getElementById("destinationInput").value;
  if (!(origin && destination)) {
    window.alert("no origin or destination selected");
    return;                // hren
    }
  document.getElementById('startingPoint').innerHTML = startingPoint;
  document.getElementById('destination').innerHTML = destination;
}

function postRide() {
    if (!(origin && destination)) {
        window.alert("no origin or destination selected");
        return;                                                // can't let the modal close
    }
    var rideTime = document.getElementById("rideTimeInput").value;
    if (rideTime.length <= 0) {
        window.alert("Please Input The Correct Time");
        return;                                                // can't let the modal close
    }
    var date = new Date(rideTime);
    rideTimeMilli = date.getTime() + 3600 * 4 * 1000;
    if (rideTimeMilli < (new Date()).getTime()) {
        window.alert("Please enter the future time");
        return;
    }
    //post the ride to the server
    var postRideReq;
    if (window.XMLHttpRequest) {
        postRideReq = new XMLHttpRequest();
    } else {
        postRideReq = new ActiveXObject("Microsoft.XMLHTTP");
    }

    postRideReq.onreadystatechange = function() {
        if (postRideReq.readyState != 4 || postRideReq.status != 200) {
            return;
        }
        //implement this
        var response = JSON.parse(postRideReq.responseText);
        var status = response[0]['status'];
        if (!status) {
            window.alert(response[0]["info"]);
            return;
        } else {
            window.alert(response[0]["info"]);
        }

        var rideType = document.getElementById("rideTypeSelect").value;
        var list;
        var ride = response[0];
        if (rideType == "Passenger") {
            list = document.getElementById("passengerList");
        } else {
            list = document.getElementById("driverList");
        }

        addPostToList(ride, list);
    }
    
    postRideReq.open("POST", "/post-ride", true);
    postRideReq.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    var request = constructPostRideRequest();

    var token = getCSRFToken();
    postRideReq.send(request + "&csrfmiddlewaretoken="+token);
}
function constructPostRideRequest() {
    var originID = origin.place_id;
    var originName = origin.name;
    var originLng = origin.geometry.location.lng();
    var originLat = origin.geometry.location.lat();

    var destinationID = destination.place_id;
    var destinationName = destination.name;
    var destinationLng = destination.geometry.location.lng();
    var destinationLat = destination.geometry.location.lat();
    var rideTime = document.getElementById("rideTimeInput").value;
    var date = new Date(rideTime);
    rideTimeMilli = date.getTime() + 3600 * 4 * 1000;
    var originImg;
    var destinationImg;
    if (origin.photos) {
        originImg = origin.photos[0].getUrl({'maxWidth': 460, 'maxHeight': 345});
    } else {
        //this is the default img
        originImg = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTa0hQb4R2hdYYQfXfaKNimW20Qg7L1GlxA8vk04kjhkbyU5tl8";
    }
    if (destination.photos) {
        destinationImg = destination.photos[0].getUrl({'maxWidth': 460, 'maxHeight': 345});
    } else {
        //this is default img
        destinationImg = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTa0hQb4R2hdYYQfXfaKNimW20Qg7L1GlxA8vk04kjhkbyU5tl8";
    }
    var originReviews;
    var destinationReviews;
    if (origin.reviews) {
        // originReviews = JSON.stringify(origin.reviews).replace(/[^a-zA-Z0-9{}\":,'_\[\]./]/g, ' ');
        originReviews = JSON.stringify(convertReviews(origin.reviews));
    }
    if (destination.reviews) {
        destinationReviews = JSON.stringify(convertReviews(destination.reviews));
        // destinationReviews = JSON.stringify(destination.reviews).replace(/[^a-zA-Z0-9{}\":,'_\[\]./]/g, ' ');
    }
    var rideType = document.getElementById("rideTypeSelect").value;
    var message = document.getElementById("id_message").value;
    if (!message) {
        message = "Nothing."
    }
    var request = "originID=" + originID +"&originName=" + originName + 
                "&originLat=" + originLat + "&originLng=" + originLng + "&originImg=" + originImg + 
                "&originReviews=" + originReviews +  
                "&originAddress=" + origin.formatted_address + 
                "&destinationID=" + destinationID + "&destinationName=" + 
                destinationName +  "&destinationLat=" + destinationLat + 
                "&destinationLng=" + destinationLng +"&destinationImg=" + destinationImg + 
                "&destinationReviews=" + destinationReviews + 
                "&destinationAddress=" + destination.formatted_address +
                 "&rideTime=" + rideTimeMilli + "&rideType=" + rideType + 
                "&message=" +　message;
    return request;
}
function convertReviews(reviews) {
    var result = [];
    for (var i = 0; i < reviews.length; i++) {
        var j = {};
        var review = reviews[i];
        j["author_name"] = review["author_name"];
        j["rating"] = review["rating"];
        j["time"] = review["time"];
        j["text"] = review["text"].replace(/[^a-zA-Z0-9,.\'+-]/g, ' ');
        result.push(j);
    }
    return result;
}
function getCSRFToken() {
    var cookies = document.cookie.split(";");
    for (var i = 0; i < cookies.length; i++) {
        if (cookies[i].startsWith("csrftoken=")) {
            return cookies[i].substring("csrftoken=".length, cookies[i].length);
        }
    }
    return "unknown";
}
function sendAcceptRideRequest(username, rideId, rideType) {
    var acceptRideRequst;
    if (window.XMLHttpRequest) {
        acceptRideRequst = new XMLHttpRequest();
    } else {
        acceptRideRequst = new ActiveXObject("Microsoft.XMLHTTP");
    }

    acceptRideRequst.onreadystatechange = function() {
        if (acceptRideRequst.readyState != 4 || acceptRideRequst.status != 200) {
            return;
        }
        var response = JSON.parse(acceptRideRequst.responseText);
        var status = response[0]['status'];
        if (!status) {
            window.alert(response[0]["info"]);
            return;
        } else {
            window.alert(response[0]["info"]);
        }

    }
    var parameters = "requestType=accept&username=" + username + "&rideId=" + rideId
                    + "&rideType=" + rideType
    acceptRideRequst.open("GET", "/process-acceptRide-request?" + parameters, true);
    acceptRideRequst.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    acceptRideRequst.send();
}


function sendConfirmRideRequest(username, rideId, rideType, messageId, thisButton) {
    var confirmRideRequst;
    var button = thisButton;
    if (window.XMLHttpRequest) {
        confirmRideRequst = new XMLHttpRequest();
    } else {
        confirmRideRequst = new ActiveXObject("Microsoft.XMLHTTP");
    }

    confirmRideRequst.onreadystatechange = function() {
        if (confirmRideRequst.readyState != 4 || confirmRideRequst.status != 200) {
            return;
        }
        var response = JSON.parse(confirmRideRequst.responseText);
        var status = response[0]['status'];
        if (!status) {
            window.alert(response[0]["info"]);
            return;
        } else {
            window.alert(response[0]["info"]);
        }

        button.parentNode.parentNode.remove();
        var newMessageCount = document.getElementById("newMessageCount");
        var count = parseInt(newMessageCount.innerHTML);
        count -= 1;
        if (count >= 0) {
            newMessageCount.innerHTML = count;
        }
    }
    var parameters = "requestType=accept&username=" + username + "&rideId=" + rideId
                    + "&rideType=" + rideType + "&messageId=" + messageId
    confirmRideRequst.open("GET", "/process-confirmRide-request?" + parameters, true);
    confirmRideRequst.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    confirmRideRequst.send();
}

function sendIgnoreMessageRequest(messageId, receiverUsername, messageType, rideId, rideType, thisButton) {
    var ignoreMessageRequest;
    var button = thisButton;
    if (window.XMLHttpRequest) {
        ignoreMessageRequest = new XMLHttpRequest();
    } else {
        ignoreMessageRequest = new ActiveXObject("Microsoft.XMLHTTP");
    }

    ignoreMessageRequest.onreadystatechange = function() {
        if (ignoreMessageRequest.readyState != 4 || ignoreMessageRequest.status != 200) {
            return;
        }
        var response = JSON.parse(ignoreMessageRequest.responseText);
        var status = response[0]['status'];
        if (!status) {
            window.alert(response[0]["info"]);
            return;
        }
        button.parentNode.parentNode.remove();
        var newMessageCount = document.getElementById("newMessageCount");
        var count = parseInt(newMessageCount.innerHTML);
        count -= 1;
        if (count >= 0) {
            newMessageCount.innerHTML = count;
        }
    }
    var parameters = "messageId=" + messageId + "&receiverUsername=" + receiverUsername +
                    "&messageType=" + messageType + "&rideId=" + rideId + "&rideType=" + rideType
    ignoreMessageRequest.open("GET", "/process-ignoreMessage-request?" + parameters, true);
    ignoreMessageRequest.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    ignoreMessageRequest.send();
}
//this function will be called to send a friend invitation to specified username
function sendAddFriendRequest(username) {
    var addFriendRequest;
    if (window.XMLHttpRequest) {
        addFriendRequest = new XMLHttpRequest();
    } else {
        addFriendRequest = new ActiveXObject("Microsoft.XMLHTTP");
    }

    addFriendRequest.onreadystatechange = function() {
        if (addFriendRequest.readyState != 4 || addFriendRequest.status != 200) {
            return;
        }
        var response = JSON.parse(addFriendRequest.responseText);
        var status = response[0]['status'];
        if (!status) {
            window.alert(response[0]["info"]);
            return;
        } else {
            window.alert(response[0]["info"]);
        }
    }
    var request = "username=" + username
    var token = getCSRFToken();
    addFriendRequest.open("POST", "/process-addFriend-request", true);
    addFriendRequest.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    addFriendRequest.send(request + "&csrfmiddlewaretoken="+token);
}
//this function will be called via a button, the button calling this function will be passed
function sendConfirmFriendRequest(messageId, thisButton) {
    var confirmAddFriendRequest;
    var button = thisButton;
    if (window.XMLHttpRequest) {
        confirmAddFriendRequest = new XMLHttpRequest();
    } else {
        confirmAddFriendRequest = new ActiveXObject("Microsoft.XMLHTTP");
    }

    confirmAddFriendRequest.onreadystatechange = function() {
        if (confirmAddFriendRequest.readyState != 4 || confirmAddFriendRequest.status != 200) {
            return;
        }
        var response = JSON.parse(confirmAddFriendRequest.responseText);
        var status = response[0]['status'];
        if (!status) {
            window.alert(response[0]["info"]);
            return;
        } else {
            window.alert(response[0]["info"]);
        }
        button.parentNode.parentNode.remove();
        var newMessageCount = document.getElementById("newMessageCount");
        var count = parseInt(newMessageCount.innerHTML);
        count -= 1;
        if (count >= 0) {
            newMessageCount.innerHTML = count;
        }
    }
    var request = "messageId=" + messageId
    var token = getCSRFToken();
    confirmAddFriendRequest.open("POST", "/process-confirmFriend-request", true);
    confirmAddFriendRequest.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    confirmAddFriendRequest.send(request + "&csrfmiddlewaretoken="+token);
}

function sendCancelRideRequest(rideId, rideType, thisButton) {
    var cancelRideRequest;
    var button = thisButton;
    if (window.XMLHttpRequest) {
        cancelRideRequest = new XMLHttpRequest();
    } else {
        cancelRideRequest = new ActiveXObject("Microsoft.XMLHTTP");
    }

    cancelRideRequest.onreadystatechange = function() {
        if (cancelRideRequest.readyState != 4 || cancelRideRequest.status != 200) {
            return;
        }
        var response = JSON.parse(cancelRideRequest.responseText);
        var status = response[0]['status'];
        if (!status) {
            window.alert(response[0]["info"]);
            return;
        } else {
            window.alert(response[0]["info"]);
        }

        button.disabled = true;
        button.innerHTML = "Canceled"

    }
    var request = "rideId=" + rideId + "&rideType=" + rideType
    var token = getCSRFToken();
    cancelRideRequest.open("POST", "/process-cancelRide-request", true);
    cancelRideRequest.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    cancelRideRequest.send(request + "&csrfmiddlewaretoken="+token);
}




var $table = $('table.scroll'),
  $bodyCells = $table.find('tbody tr:first').children(),
  colWidth;

// Adjust the width of thead cells when window resizes
$(window).resize(function() {
  // Get the tbody columns width array
  colWidth = $bodyCells.map(function() {
    return $(this).width();
  }).get();
  
  // Set the width of thead columns
  $table.find('thead tr').children().each(function(i, v) {
    $(v).width(colWidth[i]);
  });    
}).resize(); // Trigger resize handler

// popover hren
$(function() {
  
  var createPopover = function (item, title) {
                       
        var $pop = $(item);
        
        $pop.popover({
            placement: 'left',
            title: ( title || '&nbsp;' ) + ' <a class="close" href="#">&times;</a>',
            trigger: 'click',
            html: true,
            content: function () {
                return $('#popup-content').html();
            }
        }).on('shown.bs.popover', function(e) {
            // 'aria-describedby' is the id of the current popover
            var current_popover = '#' + $(e.target).attr('aria-describedby');
            var $cur_pop = $(current_popover);
          
            $cur_pop.find('.close').click(function(){
                $pop.popover('hide');
            });
          
            $cur_pop.find('.OK').click(function(){
                $pop.popover('hide');
            });
        });

        return $pop;
    };

  // create popover
  createPopover('#showPopover', 'Ride Details');

  
});