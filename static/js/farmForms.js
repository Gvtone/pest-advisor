function deleteDevice(deviceID) {
  $.ajax({
    url: "/delete_device", // Your Flask route for checking the username
    method: "POST",
    data: {
      deviceID: deviceID,
    },
    success: () => {
      location.reload();
    },
  });
}

// Function to show the error message in the modal
function showErrorInModal(errorMessage) {
  // Update the error message inside the modal
  $("#device-message").text(errorMessage);
}

$("#device-create").on("submit", function (event) {
  event.preventDefault();
  var id = parseInt(farmID);
  var deviceName = $("#device-name").val();
  var deviceURL = $("#device-url").val();
  var latitude = $("#latitude").val();
  var longitude = $("#longitude").val();

  // Make an AJAX request to check if the username is taken
  $.ajax({
    url: "/add_device", // Your Flask route for checking the username
    method: "POST",
    data: {
      id: id,
      deviceName: deviceName,
      deviceURL: deviceURL,
      latitude: latitude,
      longitude: longitude,
    },
    success: function (response) {
      if (response.location_missing) {
        showErrorInModal("Please select device location!");
      } else {
        location.reload();
      }
    },
  });
});

$("#seek-image").on("submit", function (event) {
  event.preventDefault();
  var deviceID = $("#device-select").val();
  document.getElementById("image-predictions").src =
    "/static/images/loading.gif";

  // Make an AJAX request to check if the username is taken
  $.ajax({
    url: "/yolo", // Your Flask route for checking the username
    method: "POST",
    data: {
      deviceID: deviceID,
    },
    success: function (response) {
      // Handle the response here
      var filename = response.filename;

      fetch("/static/predictions/" + filename + ".json")
        .then((response) => response.json())
        .then((json) => {
          for (const key in json) {
            if (json.hasOwnProperty(key)) {
              const para = document.createElement("p");
              const node = document.createTextNode(`${key}: ${json[key]}`);
              para.appendChild(node);

              para.classList.add("mb-0");

              const element = document.getElementById("detection-result");
              element.appendChild(para);
            }
          }
        });

      var imgSource = "/static/predictions/" + filename + ".png";
      document.getElementById("image-predictions").src = imgSource;

      var idFarm = parseInt(farmID);
      var idDevice = parseInt(deviceID);
      $.ajax({
        url: "/generate_report", // Your Flask route for checking the username
        method: "POST",
        data: {
          idFarm: idFarm,
          idDevice: idDevice,
        },
      });
    },
  });
});
