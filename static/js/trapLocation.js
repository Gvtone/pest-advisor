function initMap() {
  latitude = parseFloat(latitude);
  longitude = parseFloat(longitude);
  const myLatlng = { lat: latitude, lng: longitude };
  const map = new google.maps.Map(document.getElementById("map"), {
    mapId: "f6132d5740155e8c",
    mapTypeId: "satellite",
    center: myLatlng,
    zoom: 19,
    fullscreenControl: false,
    streetViewControl: false,
  });
}
