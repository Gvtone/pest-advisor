function initMap() {
  latitude = parseFloat(latitude);
  longitude = parseFloat(longitude);
  const myLatlng = { lat: latitude, lng: longitude };
  const map = new google.maps.Map(document.getElementById("trap-map"), {
    mapId: "f6132d5740155e8c",
    mapTypeId: "satellite",
    center: myLatlng,
    zoom: 19,
    fullscreenControl: false,
    streetViewControl: false,
  });

  new google.maps.Marker({
    position: myLatlng,
    map,
    title: "Your Farm",
    icon: {
      url: "/static/images/hut.png",
      scaledSize: new google.maps.Size(50, 50),
    },
    animation: google.maps.Animation.DROP,
  });

  fetch("/get_location/" + String(farmID))
    .then((response) => response.json())
    .then((data) => {
      // Now 'data' is a JavaScript array of objects that you can use
      for (let i = 0; i < data.length; i++) {
        let obj = data[i];

        marker = new google.maps.Marker({
          position: {
            lat: parseFloat(obj.Latitude),
            lng: parseFloat(obj.Longitude),
          },
          map,
          title: obj.Device_Name,
          icon: {
            url: "/static/images/solar-energy.png",
            scaledSize: new google.maps.Size(50, 50),
          },
          animation: google.maps.Animation.DROP,
        });

        marker.Circle = new google.maps.Circle({
          center: marker.getPosition(),
          radius: 10,
          map: map,
        });
      }
    })
    .catch((error) => console.error("Error:", error));

  const map2 = new google.maps.Map(document.getElementById("map"), {
    mapId: "f6132d5740155e8c",
    mapTypeId: "satellite",
    center: myLatlng,
    zoom: 19,
    fullscreenControl: false,
    streetViewControl: false,
  });

  // Create the initial InfoWindow.
  let infoWindow = new google.maps.InfoWindow({
    content: "Click the map to set device location!",
    position: myLatlng,
  });

  infoWindow.open(map2);
  // Configure the click listener.
  map2.addListener("click", (mapsMouseEvent) => {
    // Close the current InfoWindow.
    infoWindow.close();
    // Create a new InfoWindow.
    infoWindow = new google.maps.InfoWindow({
      position: mapsMouseEvent.latLng,
    });
    let coord = mapsMouseEvent.latLng.toJSON();

    infoWindow.setContent(`Latitude: ${coord.lat}; Longitude: ${coord.lng}`);
    infoWindow.open(map2);

    document.getElementById("latitude").value = coord.lat;
    document.getElementById("longitude").value = coord.lng;
  });
}

window.initMap = initMap;
