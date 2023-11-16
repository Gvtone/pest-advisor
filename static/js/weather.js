const apiKey = "82005d27a116c2880c8f0fcb866998a0";
const apiURL = "https://api.openweathermap.org/data/2.5/weather?units=metric";

let latitude = "14.2665541";
let longitude = "121.3883662";

async function checkWeather() {
  const response = await fetch(
    apiURL + `&lat=${latitude}` + `&lon=${longitude}` + `&appid=${apiKey}`
  );
  var data = await response.json();

  // Temperature
  document.querySelector("#temperature-location").innerHTML = data.name;
  document.querySelector("#temperature-reading").innerHTML =
    Math.round(data.main.temp) + " °C";
  document.querySelector("#humidity-reading").innerHTML =
    "Humidity level: " + data.main.humidity + "%";

  // Weather
  let iconCode = data.weather[0].icon;
  let weatherImage = `https://openweathermap.org/img/wn/${iconCode}@2x.png`;
  document.querySelector("#weather-image").src = weatherImage;

  document.querySelector("#weather-location").innerHTML = data.name;
  document.querySelector("#weather-description").innerHTML =
    "Currently: " + data.weather[0].description;
}

checkWeather();
