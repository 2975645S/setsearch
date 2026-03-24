// attendance
const attendButton = $("#attend-button");
const attendanceCount = $("#attendance-count");
const commentBox = $("#comment-box");
const concertId = commentBox.data("concert");
const csrfToken = $("input[name=csrfmiddlewaretoken]").val();

const ratingArea = $("#rating-area");
const stars = $("#star-rating span");
const rating = $("#rating");

function pluralize(count, word) {
    return count + ' ' + word + (count === 1 ? '' : 's');
}

attendButton.click(function () {
    $.ajax({
        url: "/api/concerts/attend",
        method: "POST",
        data: {
            concert: concertId,
            csrfmiddlewaretoken: csrfToken,
        },
        success: res => {
            ratingArea.toggleClass("d-none");
            attendButton.toggleClass("btn-success");
            attendButton.toggleClass("btn-outline-success");
            let attending = parseInt(attendanceCount.text());

            if (res.attending) {
                attending += 1;
                attendButton.text("Attended");
            } else {
                attending -= 1;
                attendButton.text("Not attended");
                rating.val(0);
                highlightStars(rating.val());
            }

            attendanceCount.text(pluralize(attending, 'attendee'));
        }
    })
});

function highlightStars(val) {
    stars.each(function () {
        const starVal = $(this).data("value");
        if (starVal <= val) {
            $(this).removeClass("bi-star").addClass("bi-star-fill");
        } else {
            $(this).removeClass("bi-star-fill").addClass("bi-star");
        }
    });
}

highlightStars(rating.val());

stars.hover(function () {
    highlightStars($(this).data("value"));
}, function () {
    highlightStars(rating.val());
});

stars.click(function () {
    const val = $(this).data("value");
    $.ajax({
        url: "/api/concerts/rate",
        method: "POST",
        data: {
            concert: concertId,
            rating: val,
            csrfmiddlewaretoken: csrfToken,
        },
        success: _ => {
            rating.val(val);
        }
    });
});

// comments
const commentsList = $("#comments-list");
const postButton = $("#post-comment");

// update comments
function success(res) {
    commentsList.html(res.html);
    commentBox.val("");
}

postButton.click(function () {
    const content = commentBox.val().trim();
    if (content.length === 0) return;

    $.ajax({
        url: "/api/concerts/comment",
        method: "POST",
        data: {
            content,
            concert: concertId,
            csrfmiddlewaretoken: csrfToken
        },
        success
    });
});

commentsList.on("click", ".delete-comment", e => {
    $.ajax({
        url: "/api/concerts/comment",
        method: "DELETE",
        // http://bugs.jquery.com/ticket/11586
        headers: {"X-CSRFToken": csrfToken},
        data: JSON.stringify({
            id: $(e.target).data("id"),
        }),
        success
    });
})

// delete
const deleteButton = $("#delete-concert");

deleteButton.click(function () {
    if (!confirm("Are you sure you want to delete this concert? This action cannot be undone.")) {
        return;
    }

    $.ajax({
        url: "/api/concerts/delete",
        method: "POST",
        data: {
            concert: concertId,
            csrfmiddlewaretoken: csrfToken,
        },
        success: _ => {
            window.location.href = window.location.pathname.split("/").slice(0, -2).join("/");
        }
    })
})