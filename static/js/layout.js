$(".sidebar ul li").on("click", function () {
  $(".sidebar ul li.active").removeClass("active");
  $(this).addClass("active");
});

$(".account-content ul li a").on("click", function () {
  $(".account-content ul li a.active").removeClass("active");
  $(this).addClass("active");
});

$(".setting-content").removeClass("d-flex");
$(".setting-content").hide();
$("#overview").addClass("d-flex");
$("#overview").show();
function showContent(contentId) {
  // Hide all content divs
  $(".setting-content").removeClass("d-flex");
  $(".setting-content").hide();

  // Show the selected content div
  $("#" + contentId).addClass("d-flex");
  $("#" + contentId).show();
}

// Account Setting

function accountMessage(successMessage) {
  $("#account-message").text(successMessage);
}

function securityMessage(errorMessage, color = "red") {
  $("#security-message").text(errorMessage);
  $("#security-message").css("color", color);
}

function deletionMessage(errorMessage) {
  $("#delete-account-message").text(errorMessage);
}

$("#account-form").on("submit", function (event) {
  event.preventDefault();
  var username = $("#username").val();
  var email = $("#email").val();
  var form = "account";

  $.ajax({
    url: "/user_setting",
    method: "POST",
    data: { username: username, email: email, form: form },
    success: function (response) {
      if (response.changed_both) {
        accountMessage("Username and email saved!");
      } else if (response.changed_username) {
        accountMessage("Username saved!");
      } else if (response.changed_email) {
        accountMessage("Email saved!");
      } else {
        accountMessage("");
      }
    },
  });
});

$("#security-form").on("submit", function (event) {
  event.preventDefault();
  var oldPassword = $("#oldPassword").val();
  var newPassword = $("#newPassword").val();
  var repeatPassword = $("#repeatPassword").val();
  var form = "security";

  $.ajax({
    url: "/user_setting",
    method: "POST",
    data: {
      oldPassword: oldPassword,
      newPassword: newPassword,
      repeatPassword: repeatPassword,
      form: form,
    },
    success: function (response) {
      if (response.wrong_password) {
        securityMessage("Wrong password!");
      } else if (response.password_different) {
        securityMessage("New passwords do not match!");
      } else {
        securityMessage("Password saved!", "green");
      }
    },
  });
});

$("#delete-account").on("submit", function (event) {
  event.preventDefault();
  var confirmPassword = $("#confirmPassword").val();
  var form = "delete-account";

  $.ajax({
    url: "/user_setting",
    method: "POST",
    data: {
      confirmPassword: confirmPassword,
      form: form,
    },
    success: function (response) {
      if (response.wrong_password) {
        showErrorInCard("Wrong password!");
      } else {
        window.location.href = "/login";
      }
    },
  });
});
