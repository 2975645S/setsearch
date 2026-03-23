import $ from 'https://cdn.jsdelivr.net/npm/jquery@4.0.0/+esm'

const attendButton = $("#attend-button");
const attendanceCount = $("#attendance-count");
const concertId = attendButton.data("concert");

const ratingArea = $("#rating-area");
const stars = $("#star-rating span");
const rating = $("#rating");

function pluralize(count, word) {
    return count + ' ' + word + (count === 1 ? '' : 's');
}

attendButton.click(function () {
    $.ajax({
        url: `/api/attend/${concertId}`,
        method: "POST",
        data: {
            csrfmiddlewaretoken: $("input[name=csrfmiddlewaretoken]").val(),
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
        url: `/api/rating/${concertId}`,
        method: "POST",
        data: {
            rating: val,
            csrfmiddlewaretoken: $("input[name=csrfmiddlewaretoken]").val(),
        },
        success: _ => {
            rating.val(val);
        }
    });
})
