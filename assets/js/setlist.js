// jquery 3 and sortablejs are already included
const setlist = $("#setlist");

setlist.sortable({
    animation: 150
});

// select2
const songInput = $("#id_song");

function createSong(id, name) {
    const child = $("<li>", {
        class: "list-group-item d-flex justify-content-between align-items-center",
        "data-id": id
    }).append(
        $("<strong>", {
            class: "me-3",
            text: name
        }),
        $("<button>", {
            class: "btn btn-sm btn-danger remove-song",
            text: "Delete"
        })
    );
    setlist.append(child);
}

songInput.on("select2:select", function (e) {
    const id = songInput.val();
    const name = $(this).text();

    // clear the selection
    songInput.val(null).trigger("change");
    createSong(id, name);
});

setlist.on("click", ".remove-song", function () {
    $(this).closest("li").remove();
});

// submitting
const updateButton = $("#update-button");
const info = $("#info");
const nameInput = $("#id_name");
const venueInput = $("#id_venue");
const dateInput = $("#id_date");
const csrfToken = $("input[name=csrfmiddlewaretoken]").val();

updateButton.click(function () {
    let data = {
        concert_id: $(this).data("concert"),
        name: nameInput.val(),
        venue_id: venueInput.select2("data")[0].id,
        date: dateInput.val(),
        setlist: JSON.stringify(setlist.children().map((i, el) => $(el).data("id")).get()),
        csrfmiddlewaretoken: csrfToken
    };

    $.ajax({
        method: "POST",
        url: "/api/concert/update",
        data,
        success: function () {
            window.location.href = window.location.pathname.split("/").slice(0, -1).join("/");
        }
    })
});