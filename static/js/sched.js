function getNextFriday() {
  // Get the current date
  let currentDate = new Date();

  // Find the current day of the week (0 = Sunday, 1 = Monday, ..., 6 = Saturday)
  let currentDay = currentDate.getDay();

  // Calculate the difference between the current day and Friday
  let daysUntilFriday = (5 - currentDay + 7) % 7;

  // Calculate the date of the next Friday
  let nextFridayDate = new Date(currentDate);
  nextFridayDate.setDate(currentDate.getDate() + daysUntilFriday);

  // Get the day and date of the next Friday
  let daysOfWeek = [
    "Sunday",
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
  ];
  let nextFridayDay = daysOfWeek[nextFridayDate.getDay()];
  let options = {
    month: "short",
    day: "numeric",
  };
  let nextFridayFormattedDate = nextFridayDate.toLocaleDateString(
    "en-US",
    options
  );

  return {
    day: nextFridayDay,
    date: nextFridayFormattedDate,
  };
}

let nextFridayInfo = getNextFriday();
document.querySelector("#replace-day").innerHTML = nextFridayInfo.day;
document.querySelector("#replace-date").innerHTML = nextFridayInfo.date;

// For next capture
function getDateTomorrow() {
  // Get the current date
  let currentDate = new Date();

  // Calculate the date for tomorrow
  let tomorrowDate = new Date(currentDate);
  tomorrowDate.setDate(currentDate.getDate() + 1);

  // Get the formatted date for tomorrow
  let options = {
    year: "numeric",
    month: "long",
    day: "numeric",
  };
  let tomorrowFormattedDate = tomorrowDate.toLocaleDateString("en-US", options);

  return tomorrowFormattedDate;
}

// Example usage capture-date
let tomorrowDate = getDateTomorrow();
document.querySelector("#capture-date").innerHTML = tomorrowDate;
