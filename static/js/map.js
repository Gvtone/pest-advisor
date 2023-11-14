function initMap() {
  const myLatlng = { lat: 14.2692, lng: 121.4099 };
  const map = new google.maps.Map(document.getElementById("map"), {
    mapId: "f6132d5740155e8c",
    center: myLatlng,
    zoom: 12,
    fullscreenControl: false,
    streetViewControl: false,
  });

  // Create the initial InfoWindow.
  let infoWindow = new google.maps.InfoWindow({
    content: "Click the map to set farm location!",
    position: myLatlng,
  });

  infoWindow.open(map);
  // Configure the click listener.
  map.addListener("click", (mapsMouseEvent) => {
    // Close the current InfoWindow.
    infoWindow.close();
    // Create a new InfoWindow.
    infoWindow = new google.maps.InfoWindow({
      position: mapsMouseEvent.latLng,
    });
    let coord = mapsMouseEvent.latLng.toJSON();

    infoWindow.setContent(`Latitude: ${coord.lat}; Longitude: ${coord.lng}`);
    infoWindow.open(map);

    document.getElementById("latitude").value = coord.lat;
    document.getElementById("longitude").value = coord.lng;
  });
}

window.initMap = initMap;
