// fix: stop automatic tag creation when typing something that doesn't exist

$.fn.select2.defaults.set('createTag', function(params) {
    const term = $.trim(params.term);
    if (!term) return null;
    return { id: term, text: term, isNew: true };
});

$.fn.select2.defaults.set('templateResult', function(data) {
    if (data.isNew) {
        return $(`<span>✚ Create "${data.text}"</span>`);
    }
    return data.text;
});
