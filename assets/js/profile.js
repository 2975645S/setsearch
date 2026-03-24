const deleteButton = $("#delete-profile");

deleteButton.click(function () {
    if (!confirm("Are you sure you want to delete your account? This action cannot be undone.")) {
        return;
    }

    $.ajax({
        url: "/profile",
        method: "DELETE",
        // http://bugs.jquery.com/ticket/11586
        headers: {"X-CSRFToken": $("input[name=csrfmiddlewaretoken]").val()},
        success: _ => {
            window.location.href = "/";
        }
    })
})