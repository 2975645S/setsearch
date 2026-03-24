// jquery 3 already included in artist.html

const select = $("#id_username");
const reset = $("form > button[type=reset]");

function updateLink(user) {
    $.ajax({
        method: "POST",
        url: `/api/artist/link`,
        data: {
            artist: $("#artist-id").data("id"),
            user,
            csrfmiddlewaretoken: $("input[name=csrfmiddlewaretoken]").val()
        }
    })
}

select.on("select2:select", function (e) {
    const user = e.params.data.id;
    updateLink(user);
});

reset.click(function () {
    // reset select2
    select.val(null).trigger("change");
    updateLink(null);
});
