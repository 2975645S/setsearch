// jquery 3 already included in artist.html

const select = $("#id_username");
const reset = $("form > button[type=reset]");
const slug = $("#artist-slug").data("slug");
const csrfToken = $("input[name=csrfmiddlewaretoken]").val();

function updateLink(username) {
    $.ajax({
        method: "POST",
        url: `/api/artist/${slug}/link`,
        data: {
            username,
            csrfmiddlewaretoken: csrfToken
        }
    })
}

select.on("select2:select", function (e) {
    const username = e.params.data.text;
    updateLink(username);
});

reset.click(() => {
    select.val(null).trigger("change");
    updateLink(null);
});