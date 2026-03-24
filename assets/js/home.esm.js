import Fuse from 'https://cdn.jsdelivr.net/npm/fuse.js@7.1.0/dist/fuse.mjs'
import $ from 'https://cdn.jsdelivr.net/npm/jquery@4.0.0/+esm'

const artists = await fetch("/api/artists").then(res => res.json());
const fuse = new Fuse(artists, {keys: ["name"]});

const input = $("#artist-search");
const results = $("#search-results");

// update search results as the user types
input.keyup(function () {
    const query = input.val().trim();

    if (query.length === 0) {
        results.hide().empty();
        return;
    }

    const matches = fuse.search(query).slice(0, 5).map(r => r.item); // get top 5 matches
    if (!matches.length) {
        results.hide().empty();
        return;
    }

    const items = matches.map(item =>
        `<li class="list-group-item list-group-item-action">
            <a href="/artists/${item.slug}" class="text-decoration-none">${item.name}</a>
        </li>`
    ).join('');

    results.html(items).show();
});

// show the results dropdown when the input is focused
input.focus(function () {
    if (results.children().length > 0) {
        results.show();
    }
});

// hide the results dropdown when the input loses focus
input.blur(function () {
    setTimeout(() => results.hide(), 100);
})