$("#create-form").on("submit", function (event) {
  event.preventDefault();
  var farmName = $("#farm-name").val();
  var farmAddress = $("#farm-address").val();
  var farmPicture = document.getElementById("farm-image");
  var latitude = $("#latitude").val();
  var longitude = $("#longitude").val();

  var formData = new FormData();
  formData.append("farmName", farmName);
  formData.append("farmAddress", farmAddress);
  formData.append("farmPicture", farmPicture.files[0]);
  formData.append("latitude", latitude);
  formData.append("longitude", longitude);

  $.ajax({
    url: "/add_farm",
    method: "POST",
    processData: false,
    contentType: false,
    data: formData,
    success: () => {
      location.reload();
    },
  });
});

// $("#delete-form").on("submit", function (event) {
//   event.preventDefault();
//   var farmName = $("#farm-name").val();
//   var farmAddress = $("#farm-address").val();
//   var farmPicture = document.getElementById("farm-image");
//   var latitude = $("#latitude").val();
//   var longitude = $("#longitude").val();

//   var formData = new FormData();
//   formData.append("farmName", farmName);
//   formData.append("farmAddress", farmAddress);
//   formData.append("farmPicture", farmPicture.files[0]);
//   formData.append("latitude", latitude);
//   formData.append("longitude", longitude);

//   $.ajax({
//     url: "/add_farm",
//     method: "POST",
//     processData: false,
//     contentType: false,
//     data: formData,
//     success: () => {
//       location.reload();
//     },
//   });
// });
