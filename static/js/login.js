function showErrorInCard(errorMessage) {
  $("#error-message-card").text(errorMessage);
}

$("#login-form").on("submit", function (event) {
  event.preventDefault();
  var email = $("#loginEmail").val();
  var password = $("#loginPassword").val();
  var form = "first";

  $.ajax({
    url: "/check_signup",
    method: "POST",
    data: { email: email, password: password, form: form },
    success: function (response) {
      if (response.wrong_email) {
        showErrorInCard("Email or Password was incorrect!");
      } else if (response.wrong_password) {
        showErrorInCard("Email or Password was incorrect!");
      } else {
        window.location.href = "/";
      }
    },
  });
});

// Function to show the error message in the modal
function showErrorInModal(errorMessage) {
  // Update the error message inside the modal
  $("#error-message").text(errorMessage);
  // Open the modal if it's not already open
  $("#signUp").modal("show");
}

// In your Flask route, use AJAX to check if the username is taken and call showErrorInModal if it is
$("#signup-form").on("submit", function (event) {
  event.preventDefault();
  var username = $("#username").val(); // Get the username from the form
  var email = $("#signupEmail").val();
  var password = $("#signupPassword").val();
  var repeatPassword = $("#repeatPassword").val();
  var form = "second";

  // Make an AJAX request to check if the username is taken
  $.ajax({
    url: "/check_signup", // Your Flask route for checking the username
    method: "POST",
    data: {
      username: username,
      email: email,
      password: password,
      repeatPassword: repeatPassword,
      form: form,
    },
    success: function (response) {
      if (response.username_taken) {
        showErrorInModal("Username already exist!");
      } else if (response.email_taken) {
        showErrorInModal("Email is already in use!");
      } else if (response.password_different) {
        showErrorInModal("Passwords do not match!");
      } else {
        window.location.href = "/";
      }
    },
  });
});

function revealPass() {
  var x = document.getElementById("loginPassword");
  if (x.type === "password") {
    x.type = "text";
  } else {
    x.type = "password";
  }
}
