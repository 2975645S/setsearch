import $ from 'https://cdn.jsdelivr.net/npm/jquery@4.0.0/+esm'

// elements
const commentBox = $("#comment-box");
const commentsList = $("#comments-list");
const postButton = $("#post-comment");

// data
const url = "/api/comment";
const concertId = commentsList.data("concert");
const csrfToken = $("input[name=csrfmiddlewaretoken]").val();

// update comments
function success(res) {
    commentsList.html(res.html);
    commentBox.val("");
}

postButton.click(function () {
    $.ajax({
        url,
        method: "POST",
        data: {
            content: commentBox.val(),
            concert: concertId,
            csrfmiddlewaretoken: csrfToken
        },
        success
    });
});

commentsList.on("click", ".delete-comment", e => {
    $.ajax({
        url,
        method: "DELETE",
        // http://bugs.jquery.com/ticket/11586
        headers: {"X-CSRFToken": csrfToken},
        data: JSON.stringify({
            id: $(e.target).data("id"),
        }),
        success
    });
})