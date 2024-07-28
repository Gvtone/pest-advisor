$("#set-date").on("submit", function (event) {
  event.preventDefault();
  var startDate = $("#start-date").val();
  var farmID = $("#farm-id").val();

  $.ajax({
    url: "/set_date",
    method: "POST",
    data: { startDate: startDate, farmID: farmID },
    success: () => {
      location.reload();
    },
  });
});

$("#harvest-date").on("submit", function (event) {
  event.preventDefault();
  var farmID = $("#farm-id-harvest").val();
  var isHarvest = true;

  $.ajax({
    url: "/set_date",
    method: "POST",
    data: { isHarvest: isHarvest, farmID: farmID },
    success: () => {
      location.reload();
    },
  });
});
