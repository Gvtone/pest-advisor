$(".device-content").removeClass("d-flex");
$(".device-content").hide();
$("#device-overview").addClass("d-flex");
$("#device-overview").show();
function showDeviceContent(contentId) {
  // Hide all content divs
  $(".device-content").removeClass("d-flex");
  $(".device-content").hide();

  // Show the selected content div
  $("#" + contentId).addClass("d-flex");
  $("#" + contentId).show();
}
